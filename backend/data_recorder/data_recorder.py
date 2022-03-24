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
import shutil
import struct
import sys
import time
import traceback
from decimal import Decimal
from typing import Any, Dict, Final, List, Optional, Tuple

from backend.app.crud.crud_data_collect_history import CRUDDataCollectHistory
from backend.app.models.data_collect_history import DataCollectHistory
from backend.app.models.data_collect_history_handler import DataCollectHistoryHandler
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

        target_dir_full_path: str = os.path.join(os.environ["DATA_DIR"], f"{machine_id}-{target_dir}")
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

                num_of_records = DataRecorder.data_record(
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

    @staticmethod
    def record(db: Session, machine_id: str, gateway_id: str, handler_id: str) -> None:
        """バイナリデータをpklに変換して出力する。celeryタスクから実行。"""

        logger.info(f"data recording process started. target: {machine_id}_{gateway_id}_{handler_id}")

        try:
            latest_data_collect_history_handler: DataCollectHistoryHandler = (
                CRUDDataCollectHistory.select_latest_by_machine_gateway_handler_id(db, machine_id, gateway_id, handler_id)
            )
        except Exception:
            logger.exception(traceback.format_exc())
            sys.exit(1)

        sensors: List[DataCollectHistorySensor] = latest_data_collect_history_handler.data_collect_history_sensors

        started_timestamp: float = (
            latest_data_collect_history_handler.data_collect_history_gateway.data_collect_history.started_at.timestamp()
        )

        num_of_records: int = 0
        INTERVAL: Final[int] = 1
        data_dir: str = os.environ["DATA_DIR"]

        # データ収集が停止されるまで一定間隔で無限ループ実行。
        while True:
            time.sleep(INTERVAL)

            collect_status = DataRecorderService.get_collect_status(machine_id)

            # collect_statusがRECORDEDになるのは、停止ボタン押下後全てのバイナリファイルが捌けたとき。
            if collect_status == common.COLLECT_STATUS.RECORDED.value:
                logger.info(f"data recording process stopped. machine_id: {machine_id}")
                break

            # 対象機器のファイルリストを作成
            files_info: List[FileInfo] = FileManager.create_files_info(data_dir, machine_id, gateway_id, handler_id, "dat")

            # バイナリファイルが未生成のタイミングはあり得る（例えばネットワーク遅延等）
            if len(files_info) == 0:
                logger.debug(f"No files in {data_dir}")
                continue

            # NOTE: 生成中のファイルを読み込まないよう、安全バッファとして3秒待つ
            time.sleep(3)

            num_of_records = DataRecorder.data_record(
                latest_data_collect_history_handler, files_info, Decimal(started_timestamp), num_of_records, sensors
            )

    @staticmethod
    def data_record(
        data_collect_history_handler: DataCollectHistoryHandler,
        target_files: List[FileInfo],
        started_timestamp: Decimal,
        num_of_records: int,
        sensors: List[DataCollectHistorySensor],
        is_manual: bool = False,
    ) -> int:
        """バイナリファイル読み取りおよびES/pkl出力"""

        sequential_number: int = num_of_records
        # プロセス跨ぎを考慮した時刻付け
        sampling_interval: Decimal = Decimal(1.0 / data_collect_history_handler.sampling_frequency)
        timestamp: Decimal = started_timestamp + sequential_number * sampling_interval

        for file in target_files:
            # バイナリファイルを読み取り、データリストを取得
            samples: List[Dict[str, Any]]
            samples, sequential_number, timestamp = DataRecorder.read_binary_files(
                file,
                sequential_number,
                timestamp,
                sensors,
                sampling_interval,
            )

            # pklファイルに出力
            processed_dir_path = data_collect_history_handler.data_collect_history_gateway.data_collect_history.processed_dir_path
            FileManager.export_to_pickle(samples, file, processed_dir_path)

            # 手動インポートでないとき（スケジュール実行のとき）、ファイルを退避する
            if not is_manual:
                shutil.move(file.file_path, processed_dir_path)

            # logger.info(f"processed: {file.file_path}, sequential_number(count): {sequential_number}")

        # 記録した件数
        return sequential_number

    @staticmethod
    def read_binary_files(
        file: FileInfo,
        sequential_number: int,
        timestamp: Decimal,
        sensors: List[DataCollectHistorySensor],
        sampling_interval: Decimal,
    ) -> Tuple[List[Dict[str, Any]], int, Decimal]:
        """バイナリファイルを読んで、そのデータをリストにして返す"""

        BYTE_SIZE: Final[int] = 8
        ROUND_DIGITS: Final[int] = 3
        SAMPLING_CH_NUM: Final[int] = len(sensors)
        ROW_BYTE_SIZE: Final[int] = BYTE_SIZE * SAMPLING_CH_NUM  # 8 byte * チャネル数
        UNPACK_FORMAT: Final[str] = "<" + "d" * SAMPLING_CH_NUM  # 5chの場合 "<ddddd"

        displacement_sensor: Optional[DataCollectHistorySensor] = common.get_cut_out_shot_sensor(sensors)
        displacement_sensor_id: Optional[str] = displacement_sensor.sensor_id if displacement_sensor is not None else None

        # TODO: 並び順の保証
        sensor_ids_other_than_displacement: List[str] = [
            s.sensor_id for s in sensors if s.sensor_type_id not in common.CUT_OUT_SHOT_SENSOR_TYPES
        ]

        dataset_number: int = 0  # ファイル内での連番
        samples: List[Dict[str, Any]] = []

        with open(file.file_path, "rb") as f:
            binary: bytes = f.read()

        # バイナリファイルからチャネル数分を1setとして取得し、処理
        while True:
            start_index: int = dataset_number * ROW_BYTE_SIZE
            end_index: int = start_index + ROW_BYTE_SIZE
            binary_dataset: bytes = binary[start_index:end_index]

            if len(binary_dataset) == 0:
                break

            dataset: Tuple[Any, ...] = struct.unpack(UNPACK_FORMAT, binary_dataset)
            logger.debug(dataset)

            sample: Dict[str, Any] = {
                "sequential_number": sequential_number,
                "timestamp": timestamp,
            }

            if displacement_sensor_id is not None:
                sample[displacement_sensor_id] = round(dataset[0], ROUND_DIGITS)
                # 変位センサー以外のセンサー
                for i, s in enumerate(sensor_ids_other_than_displacement):
                    sample[s] = round(dataset[i + 1], ROUND_DIGITS)
            else:
                for i, s in enumerate(sensor_ids_other_than_displacement):
                    sample[s] = round(dataset[i], ROUND_DIGITS)

            samples.append(sample)

            dataset_number += 1
            sequential_number += 1

            # NOTE: 100kサンプリングの場合10μ秒(=0.00001秒=1e-5秒)
            timestamp += sampling_interval

        return samples, sequential_number, timestamp


# manual record
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
