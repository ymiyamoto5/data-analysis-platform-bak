import os
import re
import time
from typing import Final, List, Match, Optional, Pattern, Union

import mlflow  # type: ignore
import pandas as pd
from backend.app.crud.crud_data_collect_history import CRUDDataCollectHistory
from backend.app.crud.crud_machine import CRUDMachine
from backend.app.db.session import SessionLocal
from backend.app.models.data_collect_history import DataCollectHistory
from backend.app.models.machine import Machine
from backend.app.models.sensor import Sensor
from backend.app.worker.celery import celery_app
from backend.common import common
from backend.common.common_logger import logger
from backend.data_reader.data_reader import DataReader
from backend.elastic_manager.elastic_manager import ElasticManager
from backend.utils.extract_features_by_shot import eval_dsl, extract_features
from celery import current_task
from pandas.core.frame import DataFrame
from pandas.core.series import Series


@celery_app.task()
def predictor_task(machine_id: str):
    """metaインデックスのpredictedがfalse（未予測）のショットを取得し、予測する。
    未予測のショットがないことが10回続いた場合は終了。
    """

    current_task.update_state(state="PROGRESS", meta={"message": f"predictor start. machine_id: {machine_id}"})

    logger.info(f"predictor process started. machine_id: {machine_id}")

    db = SessionLocal()
    machine: Machine = CRUDMachine.select_by_id(db, machine_id)
    if machine.auto_predict is False:
        db.close()
        return
    data_collect_history: DataCollectHistory = CRUDDataCollectHistory.select_latest_by_machine_id(db, machine_id)

    # yyyyMMddhhmmss文字列を取得
    basename: str = os.path.basename(data_collect_history.processed_dir_path)
    pattern: Pattern = re.compile(".*-(\d{14})")
    pattern_match: Union[Match[str], None] = pattern.match(basename)
    if pattern_match is None:
        db.close()
        return
    else:
        target_dir: str = pattern_match.group(1)

    meta_index = f"shots-{machine_id}-{target_dir}-meta"

    INTERVAL: Final[int] = 5
    RETRY_THRESHOLD: Final[int] = 10
    retry_count: int = 0
    while True:
        time.sleep(INTERVAL)
        # はじめにリトライカウントをチェック。しきい値を超えている場合はタスクステータスをSUCCESSとして無限ループを終了。
        if retry_count > RETRY_THRESHOLD:
            logger.info(f"[predictor] The maximum number of retries({retry_count}) has been reached.")
            logger.info(f"predictor process end. machine_id: {machine_id}")
            break
        # 未予測ショットの取得
        unpredicted_shots_meta: List[dict] = fetch_unpredicted_shots_meta(meta_index)
        if not unpredicted_shots_meta:
            _db = SessionLocal()
            _machine: Machine = CRUDMachine.select_by_id(_db, machine_id)
            collect_status: str = _machine.collect_status
            _db.close()
            # COLLECT_STATUSがSTOPであればリトライカウントインクリメント
            if collect_status == common.COLLECT_STATUS.STOP.value:
                retry_count += 1
                logger.info(f"[predictor] There are no unpredicted shots yet. retry_count: {retry_count}")
            continue

        retry_count = 0

        logger.info("[predictor] Fetch shot meta data completed.")

        # 1ショットずつデータを取得し、特徴抽出
        dr = DataReader()
        data_index = f"shots-{machine_id}-{target_dir}-data"
        features_df = pd.DataFrame()
        for shot_meta in unpredicted_shots_meta:
            shot_df = dr.read_shot(data_index, shot_meta["shot_number"])
            features = feature_extract(machine, target_dir, shot_df)
            features = features.rename(shot_meta["shot_number"])
            features_df = features_df.append(features)
            logger.info(f"[predictor] feature extracted by shot_number: {shot_meta['shot_number']}")

        if not features_df.empty:
            predict(machine, features_df, target_dir, unpredicted_shots_meta, meta_index)
            logger.info("[predictor] predict by loop finished.")

    db.close()
    return f"preditor task finished. machine_id: {machine_id}"


def fetch_unpredicted_shots_meta(meta_index: str) -> List[dict]:
    """未予測のショットメタデータをElasticsearchから取得する"""

    # meta_indexが0件だとクエリが失敗するため、先にチェック
    if ElasticManager.count(meta_index) == 0:
        return []

    label = "predicted"
    query = {"query": {"term": {label: {"value": "false"}}}, "sort": {"shot_number": {"order": "asc"}}}
    metas = ElasticManager.get_docs_with_id(index=meta_index, query=query)

    return metas


def feature_extract(machine: Machine, target_dir: str, shot_df: DataFrame) -> Series:
    """ショットデータから特徴量抽出"""

    # DSLの取得
    sensors: List[Sensor] = machine.sensors

    feature_entry: dict = {}
    for sensor in sensors:
        dsl_names: List[str] = [key for key in vars(sensor).keys() if "_dsl" in key]
        # DSLの適用
        for dsl_name in dsl_names:
            feature_name: str = dsl_name.split("_")[0]
            dsl: str = getattr(sensor, dsl_name)
            if dsl is None:
                continue
            # TODO: extract_featuresが対象をload01-04に固定しているため変更する必要有
            arg, val, _ = extract_features(shot_df, 80.0, eval_dsl, sub_func=None, dslstr=dsl)
            sensor_index_dict: dict = {k: i for i, k in enumerate(["load01", "load02", "load03", "load04"])}
            sensor_index: int = sensor_index_dict[sensor.sensor_name]
            # ELSに格納
            els_entry: dict = {
                "shot_number": shot_df.shot_number[0],
                "load": sensor.sensor_name,
                "sequential_number_by_shot": shot_df.sequential_number_by_shot[arg[sensor_index]],
                "timestamp": shot_df.timestamp[arg[sensor_index]],
                "value": val[sensor_index],
                "sequential_number": shot_df.sequential_number[arg[sensor_index]],
            }
            ind: str = f"shots-{machine.machine_id}-{target_dir}-{feature_name}-point"
            if not ElasticManager.exists_index(ind):
                ElasticManager.create_index(ind)
            ElasticManager.create_doc(ind, els_entry)
            # 予測用の特徴量
            feature_entry[f"{sensor.sensor_name}_{feature_name}-point"] = val[sensor_index]

    return pd.Series(feature_entry)
    # return pd.DataFrame.from_dict(feature_entry, orient="index").T


def predict(machine: Machine, features_df: DataFrame, target_dir: str, shot_metas: List[dict], meta_index: str) -> Optional[List[bool]]:
    """予測"""

    mlflow_server_uri: str = os.environ["mlflow_server_uri"]
    mlflow.set_tracking_uri(mlflow_server_uri)
    # machineテーブルの参照
    # モデルとバージョンの取得
    model_name: str = machine.predict_model
    if model_name is None:
        logger.error("model_name required.")
        return

    model_version: str = machine.model_version
    if model_version is None:
        logger.error("model_version required.")
        return None

    # MLFlowからモデルの取得
    model = mlflow.sklearn.load_model(model_uri=f"models:/{model_name}/{model_version}")

    # 予測の実行
    if not all(map(lambda x: x in features_df.columns, model.feature_names_in_)):
        return None
    features_df = features_df.reindex(columns=model.feature_names_in_)
    results: List[bool] = model.predict(features_df)

    els_entries = []
    for [df_index, feature], result in zip(features_df.iterrows(), results):
        els_entry: dict = {"shot_number": df_index, "model": model_name, "version": model_version}
        els_entry.update(feature.to_dict())
        els_entry["label"] = result
        els_entries.append(els_entry)

    # ELSに格納(予測結果＋予測済みフラグ)
    predict_index: str = f"shots-{machine.machine_id}-{target_dir}-predict"
    if not ElasticManager.exists_index(predict_index):
        ElasticManager.create_index(predict_index)
    ElasticManager.bulk_insert(els_entries, predict_index)

    # MetaのPredictedを更新
    for target_shot in features_df.index:
        shot_ids = [meta["id"] for meta in shot_metas if meta["shot_number"] == target_shot]
        if shot_ids:
            ElasticManager.update_doc(meta_index, shot_ids[0], {"predicted": True})

    return results
