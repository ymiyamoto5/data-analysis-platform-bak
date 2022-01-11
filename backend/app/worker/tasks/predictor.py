import os
import re
import time
from typing import Final, List, Match, Pattern, Tuple, Union

import mlflow  # type: ignore
import pandas as pd
from backend.app.crud.crud_data_collect_history import CRUDDataCollectHistory
from backend.app.crud.crud_machine import CRUDMachine
from backend.app.db.session import SessionLocal
from backend.app.models.data_collect_history import DataCollectHistory
from backend.app.models.machine import Machine
from backend.app.models.sensor import Sensor
from backend.app.worker.celery import celery_app
from backend.common.common_logger import logger
from backend.data_reader.data_reader import DataReader
from backend.elastic_manager.elastic_manager import ElasticManager
from backend.utils.extract_features_by_shot import eval_dsl, extract_features
from pandas.core.frame import DataFrame


@celery_app.task(acks_late=True)
def predictor_task(machine_id: str):

    logger.info(f"predictor process started. machine_id: {machine_id}")

    db = SessionLocal()
    machine: Machine = CRUDMachine.select_by_id(db, machine_id)
    if machine.auto_predict is False:
        db.close()
        return
    data_collect_history: DataCollectHistory = CRUDDataCollectHistory.select_latest_by_machine_id(db, machine_id)

    basename: str = os.path.basename(data_collect_history.processed_dir_path)
    pattern: Pattern = re.compile(".*-(\d{14})")
    pattern_match: Union[Match[str], None] = pattern.match(basename)
    if pattern_match is None:
        db.close()
        return
    else:
        target_dir: str = pattern_match.group(1)

    INTERVAL: Final[int] = 5
    RETRY_THRESHOLD: Final[int] = 10
    retry_count: int = 0
    while True:
        time.sleep(INTERVAL)

        shot_df, target_shot = fetch_shot_data(machine_id, target_dir)
        if shot_df is None:
            retry_count += 1
            if retry_count > RETRY_THRESHOLD:
                logger.info(f"[predictor] The maximum number of retries({retry_count}) has been reached.")
                logger.info(f"predictor process end. machine_id: {machine_id}")
                break
            else:
                continue
        else:
            retry_count = 0

        logger.info(f"[predictor] Fetch shot data completed. Target shot is {target_shot}.")
        features = feature_extract(machine, target_dir, shot_df)
        if not features.empty:
            predict(machine, features, target_dir, target_shot)

    db.close()


def fetch_shot_data(machine_id: str, target_dir: str) -> Tuple[DataFrame, int]:

    data_index = f"shots-{machine_id}-{target_dir}-data"
    meta_index = f"shots-{machine_id}-{target_dir}-meta"

    label = "predicted"
    agg_name = "predict_shotnum"
    query = {"query": {"term": {label: {"value": "false"}}}, "aggs": {agg_name: {"min": {"field": "shot_number"}}}}
    aggs = ElasticManager.es.search(index=meta_index, body=query)["aggregations"]

    # TODO: すべて予測済みの場合のreturn処理追加
    if aggs[agg_name]["value"] is None:
        return [None, None]

    dr = DataReader()
    target_shot = int(aggs[agg_name]["value"])
    shot_df = dr.read_shot(data_index, shot_number=target_shot)
    return (shot_df, target_shot)


def feature_extract(machine: Machine, target_dir: str, shot_df: DataFrame) -> DataFrame:
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
            # extract_featuresが対象をload01-04に固定しているため変更する必要有
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

    return pd.DataFrame.from_dict(feature_entry, orient="index").T


def predict(machine: Machine, features: DataFrame, target_dir: str, target_shot: int) -> bool:
    mlflow_server_uri: str = os.environ["mlflow_server_uri"]
    mlflow.set_tracking_uri(mlflow_server_uri)
    # machineテーブルの参照
    # モデルとバージョンの取得
    model_name: str = machine.predict_model
    model_version: str = machine.model_version

    # MLFlowからモデルの取得
    model = mlflow.sklearn.load_model(model_uri=f"models:/{model_name}/{model_version}")
    result = model.predict(features)

    # 予測の実行
    if not all(map(lambda x: x in features.columns, model.feature_names_in_)):
        return
    data: DataFrame = features.reindex(columns=model.feature_names_in_)
    result: bool = model.predict(data)[0]
    els_entry: dict = {"shot_number": target_shot, "model": model_name, "version": model_version}
    els_entry.update(data.to_dict(orient="records")[0])
    els_entry["label"] = result
    # ELSに格納(予測結果＋予測済みフラグ)
    ind: str = f"shots-{machine.machine_id}-{target_dir}-predict"
    if not ElasticManager.exists_index(ind):
        ElasticManager.create_index(ind)
    ElasticManager.create_doc(ind, els_entry)

    # MetaのPredictedを更新
    meta_index: str = f"shots-{machine.machine_id}-{target_dir}-meta"
    query: dict = {"query": {"term": {"shot_number": {"value": target_shot}}}}
    meta_data: dict = ElasticManager.get_docs_with_id(meta_index, query)[0]
    ElasticManager.update_doc(meta_index, meta_data["id"], {"predicted": True})

    return result
