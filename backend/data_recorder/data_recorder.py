"""
 ==================================
  data_recorder.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import argparse
import os
import sys
import traceback
from decimal import Decimal
from typing import Any, Dict, Final, List, Optional, Tuple

from backend.app.crud.crud_data_collect_history import CRUDDataCollectHistory
from backend.app.models.data_collect_history import DataCollectHistory
from backend.app.models.data_collect_history_detail import DataCollectHistoryDetail
from backend.app.models.data_collect_history_event import DataCollectHistoryEvent
from backend.app.services.data_recorder_service import DataRecorderService
from backend.common import common
from backend.common.common_logger import data_recorder_logger as logger
from backend.file_manager.file_manager import FileInfo, FileManager
from dotenv import load_dotenv
from sqlalchemy.orm.session import Session

env_file = ".env"
load_dotenv(env_file)

API_URL: Final[str] = os.environ["API_URL"]


class DataRecorder:
    @staticmethod
    def manual_record(db: Session, machine_id: str, target_dir: str):
        """手動での生データ取り込み。前提条件は以下。
        * 取り込むデータディレクトリはdataフォルダ配下に配置すること。
        """

        files_info: List[FileInfo] = FileManager.create_files_info(target_dir, machine_id, "dat")

        if len(files_info) == 0:
            logger.info(f"No files in {target_dir}")
            return

        target_datetime_str: str = target_dir.split("-")[-1]

        try:
            data_collect_history: DataCollectHistory = CRUDDataCollectHistory.select_by_machine_id_started_at(
                db, machine_id, target_datetime_str
            )
        except Exception:
            logger.exception(traceback.format_exc())
            sys.exit(1)

        if data_collect_history.data_collect_history_events[-1].event_name != common.COLLECT_STATUS.RECORDED.value:
            logger.error(f"Latest event should be '{common.COLLECT_STATUS.RECORDED.value}'.")
            sys.exit(1)

        sensors: List[DataCollectHistoryDetail] = data_collect_history.data_collect_history_details
        displacement_sensor: List[DataCollectHistoryDetail] = [s for s in sensors if s.sensor_type_id in common.CUT_OUT_SHOT_SENSOR_TYPES]

        # 変位センサーは機器にただひとつのみ紐づいている前提
        if len(displacement_sensor) != 1:
            logger.error(f"Only one displacement sensor is needed. num_of_displacement_sensor: {displacement_sensor}")
            sys.exit(1)

        displacement_sensor_id: str = displacement_sensor[0].sensor_id

        # TODO: 並び順の保証
        sensor_ids_other_than_displacement: List[str] = [
            s.sensor_id for s in sensors if s.sensor_type_id not in common.CUT_OUT_SHOT_SENSOR_TYPES
        ]

        started_timestamp: float = data_collect_history.started_at.timestamp()

        num_of_records: int = 0

        num_of_records = DataRecorderService.data_record(
            data_collect_history,
            files_info,
            Decimal(started_timestamp),
            num_of_records,
            displacement_sensor_id,
            sensor_ids_other_than_displacement,
            is_manual=True,
        )

        logger.info("manual import finished.")


if __name__ == "__main__":
    from backend.app.db.session import SessionLocal  # noqa

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", help="set import directory (manual import)", required=True)
    # NOTE: 未使用
    parser.add_argument("--debug", action="store_true", help="debug mode")
    args = parser.parse_args()

    target_dir: str = os.path.join(os.environ["data_dir"], args.dir)

    if not os.path.isdir(target_dir):
        logger.error(f"{target_dir} is not exists.")
        sys.exit(1)

    machine_id = "-".join(args.dir.split("-")[:-1])
    db: Session = SessionLocal()
    DataRecorder.manual_record(db, machine_id, target_dir)
    db.close()
