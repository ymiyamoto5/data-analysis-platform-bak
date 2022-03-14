"""
 ==================================
  data_recorder.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import argparse
import glob
import os
import sys
import traceback
from decimal import Decimal
from typing import List

from backend.app.crud.crud_data_collect_history import CRUDDataCollectHistory
from backend.app.models.data_collect_history import DataCollectHistory
from backend.app.models.data_collect_history_sensor import DataCollectHistorySensor
from backend.app.services.data_recorder_service import DataRecorderService
from backend.common import common
from backend.common.common_logger import data_recorder_logger as logger
from backend.file_manager.file_manager import FileInfo, FileManager
from sqlalchemy.orm.session import Session


class DataRecorder:
    @staticmethod
    def manual_record(db: Session, machine_id: str, target_dir: str):
        """手動での生データ取り込み。前提条件は以下。
        * 取り込むデータディレクトリはdataフォルダ配下に配置すること。
        """

        try:
            data_collect_history: DataCollectHistory = CRUDDataCollectHistory.select_by_machine_id_target_dir(db, machine_id, target_dir)
            sensors: List[DataCollectHistorySensor] = CRUDDataCollectHistory.select_cut_out_target_sensors_by_history_id(
                db, data_collect_history.id
            )
        except Exception:
            logger.exception(traceback.format_exc())
            sys.exit(1)

        target_dir_full_path: str = os.path.join(os.environ["data_dir"], f"{machine_id}-{target_dir}")
        # 既存のpickleファイルは削除する
        pickle_files: List[str] = glob.glob(os.path.join(target_dir_full_path, "*.pkl"))
        if len(pickle_files):
            while True:
                choice = input("The pickle files already exist. Do you want to delete it? 'yes' or 'no' [y/N]: ").lower()
                if choice in ["y", "yes"]:
                    break
                elif choice in ["n", "no"]:
                    logger.info("実行をキャンセルしました")
                    sys.exit(1)
            for file in pickle_files:
                os.remove(file)

        for gateway in data_collect_history.data_collect_history_gateways:
            for handler in gateway.data_collect_history_handlers:
                files_info: List[FileInfo] = FileManager.create_files_info(
                    target_dir_full_path, machine_id, gateway.gateway_id, handler.handler_id, "dat"
                )

                if len(files_info) == 0:
                    logger.info(f"No files in {target_dir}")
                    return

                if data_collect_history.data_collect_history_events[-1].event_name != common.COLLECT_STATUS.RECORDED.value:
                    logger.error(f"Latest event should be '{common.COLLECT_STATUS.RECORDED.value}'.")
                    sys.exit(1)

                started_timestamp: float = data_collect_history.started_at.timestamp()
                num_of_records: int = 0

                num_of_records = DataRecorderService.data_record(
                    handler,
                    files_info,
                    Decimal(started_timestamp),
                    num_of_records,
                    sensors=sensors,
                    is_manual=True,
                )

                logger.info(f"import finished: {handler.handler_id}")
            logger.info(f"import finished: {gateway.gateway_id}")

        logger.info(f"manual import finished: {machine_id}")


if __name__ == "__main__":
    from backend.app.db.session import SessionLocal  # noqa

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", help="set import directory (manual import)", required=True)
    # NOTE: 未使用
    parser.add_argument("--debug", action="store_true", help="debug mode")
    args = parser.parse_args()

    splitted_dir: str = args.dir.split("-")
    machine_id: str = "-".join(splitted_dir[:-1])
    target_dir: str = splitted_dir[-1]

    db: Session = SessionLocal()
    DataRecorder.manual_record(db, machine_id, target_dir)
    db.close()
