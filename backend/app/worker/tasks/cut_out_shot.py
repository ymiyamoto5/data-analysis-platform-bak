import os
import sys
import time
import traceback
from typing import Final, List

from backend.app.crud.crud_data_collect_history import CRUDDataCollectHistory
from backend.app.crud.crud_machine import CRUDMachine
from backend.app.db.session import SessionLocal
from backend.app.models.data_collect_history import DataCollectHistory
from backend.app.models.machine import Machine
from backend.app.worker.celery import celery_app
from backend.common import common
from backend.common.common_logger import logger
from backend.cut_out_shot.cut_out_shot import CutOutShot
from backend.cut_out_shot.stroke_displacement_cutter import StrokeDisplacementCutter
from backend.elastic_manager.elastic_manager import ElasticManager
from backend.file_manager.file_manager import FileManager
from celery import current_task
from sqlalchemy.orm.session import Session


@celery_app.task(acks_late=True)
def cut_out_shot_task(machine_id: str) -> str:
    """オンラインショット切り出しタスク
    * DBから設定値取得
    * Elasticsearchインデックス作成
    * CutOutShotインスタンス作成
    * ループ処理
      * 処理対象特定
      * CutOutShot.auto_cut_out_shot呼び出し
    """

    current_task.update_state(state="PROGRESS", meta={"message": f"cut_out_shot start. machine_id: {machine_id}"})

    logger.info(f"cut_out_shot process started. machine_id: {machine_id}")

    db: Session = SessionLocal()

    try:
        machine: Machine = CRUDMachine.select_by_id(db, machine_id)
        latest_data_collect_history: DataCollectHistory = CRUDDataCollectHistory.select_latest_by_machine_id(db, machine_id)
    except Exception:
        logger.exception(traceback.format_exc())
        sys.exit(1)

    target_date_str: str = latest_data_collect_history.processed_dir_path.split("-")[-1]

    shots_index: str = "shots-" + target_date_str + "-data"
    setting_shots: str = os.environ["setting_shots_path"]
    ElasticManager.create_index(index=shots_index, setting_file=setting_shots)

    shots_meta_index: str = "shots-" + target_date_str + "-meta"
    setting_shots_meta: str = os.environ["setting_shots_meta_path"]
    ElasticManager.create_index(index=shots_meta_index, setting_file=setting_shots_meta)

    # TODO: pulse対応
    cutter = StrokeDisplacementCutter(
        machine.start_displacement,
        machine.end_displacement,
        margin=machine.margin,
        sensors=latest_data_collect_history.data_collect_history_details,
    )

    cut_out_shot: CutOutShot = CutOutShot(
        cutter=cutter,
        data_collect_history=latest_data_collect_history,
        machine_id=machine_id,
        target=target_date_str,
    )

    INTERVAL: Final[int] = 5
    has_been_processed: List[str] = []  # 処理済みファイルパスリスト

    while True:
        time.sleep(INTERVAL)

        # 退避ディレクトリに存在するすべてのpklファイルパスリスト
        all_files: List[str] = FileManager.get_files(dir_path=latest_data_collect_history.processed_dir_path, pattern=f"{machine_id}_*.pkl")

        # ループ毎の処理対象。未処理のもののみ対象とする。
        target_files: List[str] = get_target_files(all_files, has_been_processed)

        # NOTE: 毎度DBにアクセスするのは非効率なため、対象ファイルが存在しないときのみDBから収集ステータスを確認し、停止判断を行う。
        if len(target_files) == 0:
            collect_status = get_collect_status(machine_id)

            if collect_status == common.COLLECT_STATUS.RECORDED.value:
                logger.info(f"cut_out_shot process finished. machine_id: {machine_id}")
                break
            # 記録が完了していなければ継続
            continue

        # 切り出し処理
        logger.info(f"cut_out_shot processing. machine_id: {machine_id}, targets: {len(target_files)}")

        cut_out_shot.auto_cut_out_shot(target_files, shots_index, shots_meta_index)

    db.close()

    return f"cut_out_shot task finished. machine_id: {machine_id}"


def get_target_files(all_files: List[str], has_been_processed: List[str]) -> List[str]:
    """all_files（全ファイル）のうち、has_been_processed（処理済み）を除外したリストを返す"""
    target_files: List[str] = []

    for file in all_files:
        if file not in has_been_processed:
            target_files.append(file)

    return target_files


def get_collect_status(machine_id) -> str:
    """データ収集ステータスを取得する"""

    # NOTE: DBセッションを使いまわすと更新データが得られないため、新しいセッション作成
    db: Session = SessionLocal()
    machine: Machine = CRUDMachine.select_by_id(db, machine_id)
    collect_status: str = machine.collect_status
    db.close()

    return collect_status
