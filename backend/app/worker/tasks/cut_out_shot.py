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
def cut_out_shot_task(cut_out_shot_json: str, sensor_type: str, debug_mode: bool = False) -> str:
    """ショット切り出し画面のショット切り出しタスク
    * DBから設定値取得
    * Elasticsearchインデックス作成
    * CutOutShotインスタンス作成
    * CutOutShot.cut_out_shot_by_task呼び出し
    """

    cut_out_shot_in = json.loads(cut_out_shot_json)
    machine_id: str = cut_out_shot_in["machine_id"]
    target_date_str: str = cut_out_shot_in["target_date_str"]

    if not debug_mode:
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

    if len(cut_out_target_handlers) == 0:
        logger.error("")
        db.close()
        sys.exit(1)
    else:
        handler = common.get_main_handler(cut_out_target_handlers)

    # 切り出し処理
    cut_out_shot = CutOutShot(
        cutter=cutter,
        machine_id=machine_id,
        target=target_date_str,
        data_collect_history=history,
        sampling_frequency=handler.sampling_frequency,
        sensors=cut_out_target_sensors,
    )

    try:
        cut_out_shot.cut_out_shot(is_called_by_task=True)
    except Exception:
        logger.exception(traceback.format_exc())
        sys.exit(1)
    finally:
        db.close()

    return f"cut_out_shot task finished. machine_id: {machine_id}"


@celery_app.task()
def auto_cut_out_shot_task(machine_id: str, sensor_type: str, debug_mode: bool = False) -> str:
    """オンラインショット切り出しタスク
    * DBから設定値取得
    * Elasticsearchインデックス作成
    * CutOutShotインスタンス作成
    * ループ処理
      * 処理対象特定
      * CutOutShot.cut_out_shot_by_task呼び出し
    """

    if not debug_mode:
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

    if len(cut_out_target_handlers) == 0:
        logger.error("")
        db.close()
        sys.exit(1)
    else:
        handler = common.get_main_handler(cut_out_target_handlers)

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
        sampling_frequency=handler.sampling_frequency,
        sensors=cut_out_target_sensors,
        machine_id=machine_id,
        target=target_date_str,
    )

    INTERVAL: Final[int] = 5
    has_been_processed: List[str] = []  # 処理済みファイルパスリスト
    retry_count: int = 0
    MAX_RETRY_COUNT: Final[int] = 3
    loop_count: int = 0

    while True:
        if retry_count >= MAX_RETRY_COUNT:
            logger.error("Over max retry count. File index numbers may not be equal between handlers.")
            sys.exit(1)

        time.sleep(INTERVAL)

        loop_count += 1

        # 退避ディレクトリに存在するすべてのpklファイルパスリスト
        try:
            # logger.info(f"history.processed_dir_path: {history.processed_dir_path}")
            files: List[str] = FileManager.get_files(dir_path=history.processed_dir_path, pattern=f"{machine_id}_*.pkl")
        except Exception:
            logger.error(traceback.format_exc())
            retry_count += 1
            continue

        retry_count = 0

        if len(files) == 0:
            continue

        # ループ毎の処理対象。未処理のもののみ対象とする。
        target_files: List[str] = [x for x in files if x not in has_been_processed]

        # NOTE: 毎度DBにアクセスするのは非効率なため、対象ファイルが存在しないときのみDBから収集ステータスを確認し、停止判断を行う。
        if len(target_files) == 0:
            collect_status = get_collect_status(machine_id)

            if collect_status == common.COLLECT_STATUS.RECORDED.value:
                logger.info(f"auto_cut_out_shot process stopped. machine_id: {machine_id}")
                break
            # 記録が完了していなければ継続
            continue

        # 切り出し処理
        logger.info(f"cut_out_shot processing (loop_count: {loop_count}). machine_id: {machine_id}, targets: {len(target_files)}")
        cut_out_shot.auto_cut_out_shot(target_files, shots_index, shots_meta_index, debug_mode=debug_mode)
        logger.info(f"cut_out_shot finished (loop_count: {loop_count}). machine_id: {machine_id}, targets: {len(target_files)}")

        has_been_processed.extend(target_files)

        if debug_mode:
            break

    db.close()

    return f"auto_cut_out_shot task finished. machine_id: {machine_id}"


def create_shots_index_set(shots_index: str, shots_meta_index: str) -> None:
    """Elasticsearchインデックスを作成する"""
    ElasticManager.delete_exists_index(index=shots_index)
    setting_shots: str = os.environ["SETTING_SHOTS_PATH"]
    ElasticManager.create_index(index=shots_index, setting_file=setting_shots)

    ElasticManager.delete_exists_index(index=shots_meta_index)
    setting_shots_meta: str = os.environ["SETTING_SHOTS_META_PATH"]
    ElasticManager.create_index(index=shots_meta_index, setting_file=setting_shots_meta)


def get_collect_status(machine_id) -> str:
    """データ収集ステータスを取得する"""
    # TODO: 共通化

    # NOTE: DBセッションを使いまわすと更新データが得られないため、新しいセッション作成
    db: Session = SessionLocal()
    machine: Machine = CRUDMachine.select_by_id(db, machine_id)
    collect_status: str = machine.collect_status
    db.close()

    return collect_status
