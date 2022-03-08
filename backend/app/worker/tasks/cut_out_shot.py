import json
import os
import sys
import time
import traceback
from typing import Final, List, Union

from backend.app.crud.crud_data_collect_history import CRUDDataCollectHistory
from backend.app.crud.crud_machine import CRUDMachine
from backend.app.db.session import SessionLocal
from backend.app.models.data_collect_history import DataCollectHistory
from backend.app.models.data_collect_history_handler import DataCollectHistoryHandler
from backend.app.models.data_collect_history_sensor import DataCollectHistorySensor
from backend.app.models.machine import Machine
from backend.app.worker.celery import celery_app
from backend.common import common
from backend.common.common_logger import logger
from backend.cut_out_shot.cut_out_shot import CutOutShot
from backend.cut_out_shot.pulse_cutter import PulseCutter
from backend.cut_out_shot.stroke_displacement_cutter import StrokeDisplacementCutter
from backend.elastic_manager.elastic_manager import ElasticManager
from backend.file_manager.file_manager import FileManager
from celery import current_task
from sqlalchemy.orm.session import Session


@celery_app.task()
def cut_out_shot_task(cut_out_shot_json: str, sensor_type: str) -> str:
    """ショット切り出し画面のショット切り出しタスク
    * DBから設定値取得
    * Elasticsearchインデックス作成
    * CutOutShotインスタンス作成
    * CutOutShot.cut_out_shot_by_task呼び出し
    """

    cut_out_shot_in = json.loads(cut_out_shot_json)
    machine_id: str = cut_out_shot_in["machine_id"]
    target_date_str: str = cut_out_shot_in["target_date_str"]

    current_task.update_state(state="PROGRESS", meta={"message": f"cut_out_shot start. machine_id: {machine_id}", "progress": 0})

    logger.info(f"cut_out_shot process started. machine_id: {machine_id}")

    db: Session = SessionLocal()

    try:
        # データ収集時の履歴から、収集当時の設定値を取得する
        history: DataCollectHistory = CRUDDataCollectHistory.select_by_machine_id_started_at(db, machine_id, target_date_str)
        cut_out_target_handlers: List[DataCollectHistoryHandler] = CRUDDataCollectHistory.select_cut_out_target_handlers_by_hisotry_id(
            db, history.id
        )
        cut_out_target_sensors: List[DataCollectHistorySensor] = CRUDDataCollectHistory.select_cut_out_target_sensors_by_history_id(
            db, history.id
        )
    except Exception:
        logger.exception(traceback.format_exc())
        db.close()
        sys.exit(1)

    cutter: Union[StrokeDisplacementCutter, PulseCutter]
    if sensor_type == common.CUT_OUT_SHOT_SENSOR_TYPES[0]:
        cutter = StrokeDisplacementCutter(
            cut_out_shot_in["start_stroke_displacement"],
            cut_out_shot_in["end_stroke_displacement"],
            margin=cut_out_shot_in["margin"],
            sensors=cut_out_target_sensors,
        )
    else:
        cutter = PulseCutter(
            threshold=cut_out_shot_in["threshold"],
            sensors=cut_out_target_sensors,
        )

    # 切り出し処理
    cut_out_shot = CutOutShot(
        cutter=cutter,
        machine_id=machine_id,
        target=target_date_str,
        data_collect_history=history,
        handlers=cut_out_target_handlers,
        sensors=cut_out_target_sensors,
    )
    cut_out_shot.cut_out_shot(is_called_by_task=True)

    db.close()

    return f"cut_out_shot task finished. machine_id: {machine_id}"


@celery_app.task()
def auto_cut_out_shot_task(machine_id: str, sensor_type: str) -> str:
    """オンラインショット切り出しタスク
    * DBから設定値取得
    * Elasticsearchインデックス作成
    * CutOutShotインスタンス作成
    * ループ処理
      * 処理対象特定
      * CutOutShot.cut_out_shot_by_task呼び出し
    """

    current_task.update_state(state="PROGRESS", meta={"message": f"auto_cut_out_shot start. machine_id: {machine_id}"})

    logger.info(f"auto_cut_out_shot process started. machine_id: {machine_id}")

    db: Session = SessionLocal()

    try:
        machine: Machine = CRUDMachine.select_by_id(db, machine_id)
        history: DataCollectHistory = CRUDDataCollectHistory.select_latest_by_machine_id(db, machine_id)
        cut_out_target_handlers: List[DataCollectHistoryHandler] = CRUDDataCollectHistory.select_cut_out_target_handlers_by_hisotry_id(
            db, history.id
        )
        cut_out_target_sensors: List[DataCollectHistorySensor] = CRUDDataCollectHistory.select_cut_out_target_sensors_by_history_id(
            db, history.id
        )
    except Exception:
        logger.exception(traceback.format_exc())
        db.close()
        sys.exit(1)

    target_date_str: str = history.processed_dir_path.split("-")[-1]

    shots_index: str = f"shots-{machine_id}-{target_date_str}-data"
    shots_meta_index: str = f"shots-{machine_id}-{target_date_str}-meta"
    create_shots_index_set(shots_index, shots_meta_index)

    cutter: Union[StrokeDisplacementCutter, PulseCutter]
    if sensor_type == common.CUT_OUT_SHOT_SENSOR_TYPES[0]:
        cutter = StrokeDisplacementCutter(
            machine.start_displacement,
            machine.end_displacement,
            margin=machine.margin,
            sensors=cut_out_target_sensors,
        )
    else:
        cutter = PulseCutter(
            threshold=machine.threshold,
            sensors=cut_out_target_sensors,
        )

    cut_out_shot: CutOutShot = CutOutShot(
        cutter=cutter,
        data_collect_history=history,
        handlers=cut_out_target_handlers,
        sensors=cut_out_target_sensors,
        machine_id=machine_id,
        target=target_date_str,
    )

    INTERVAL: Final[int] = 5
    has_been_processed: List[List[str]] = []  # 処理済みファイルパスリスト

    while True:
        time.sleep(INTERVAL)

        # # 退避ディレクトリに存在するすべてのpklファイルパスリスト
        files_list: List[List[str]] = FileManager.get_files_list(machine_id, cut_out_target_handlers, history.processed_dir_path)

        # ループ毎の処理対象。未処理のもののみ対象とする。
        target_files: List[List[str]] = get_target_files(files_list, has_been_processed)

        # NOTE: 毎度DBにアクセスするのは非効率なため、対象ファイルが存在しないときのみDBから収集ステータスを確認し、停止判断を行う。
        if len(target_files) == 0:
            collect_status = get_collect_status(machine_id)

            if collect_status == common.COLLECT_STATUS.RECORDED.value:
                logger.info(f"auto_cut_out_shot process stopped. machine_id: {machine_id}")
                break
            # 記録が完了していなければ継続
            continue

        # 切り出し処理
        logger.info(f"auto_cut_out_shot processing. machine_id: {machine_id}, targets: {len(target_files)}")
        cut_out_shot.auto_cut_out_shot(target_files, shots_index, shots_meta_index)

        has_been_processed.extend(target_files)

    db.close()

    return f"auto_cut_out_shot task finished. machine_id: {machine_id}"


def create_shots_index_set(shots_index: str, shots_meta_index: str) -> None:
    """Elasticsearchインデックスを作成する"""
    ElasticManager.delete_exists_index(index=shots_index)
    setting_shots: str = os.environ["setting_shots_path"]
    ElasticManager.create_index(index=shots_index, setting_file=setting_shots)

    ElasticManager.delete_exists_index(index=shots_meta_index)
    setting_shots_meta: str = os.environ["setting_shots_meta_path"]
    ElasticManager.create_index(index=shots_meta_index, setting_file=setting_shots_meta)


def get_target_files(all_files: List[List[str]], has_been_processed: List[List[str]]) -> List[List[str]]:
    """all_files（全ファイル）のうち、has_been_processed（処理済み）を除外したリストを返す"""

    target_files: List[List[str]] = []

    # ハンドラーごとのリスト、つまり[[ADC1_1.dat, ADC2_1.dat, ...], [ADC1_2.dat, ADC2_2.dat, ...]] になっている
    for handlers_file in all_files:
        if handlers_file not in has_been_processed:
            target_files.append(handlers_file)

    return target_files


def get_collect_status(machine_id) -> str:
    """データ収集ステータスを取得する"""
    # TODO: 共通化

    # NOTE: DBセッションを使いまわすと更新データが得られないため、新しいセッション作成
    db: Session = SessionLocal()
    machine: Machine = CRUDMachine.select_by_id(db, machine_id)
    collect_status: str = machine.collect_status
    db.close()

    return collect_status
