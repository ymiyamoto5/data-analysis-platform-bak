import os
import shutil
import struct
import sys
import time
import traceback
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, Final, List, Optional, Tuple

from backend.app.crud.crud_data_collect_history import CRUDDataCollectHistory
from backend.app.crud.crud_machine import CRUDMachine
from backend.app.db.session import SessionLocal
from backend.app.models.data_collect_history import DataCollectHistory
from backend.app.models.data_collect_history_detail import DataCollectHistoryDetail
from backend.app.models.machine import Machine
from backend.common import common
from backend.common.common_logger import logger
from backend.file_manager.file_manager import FileInfo, FileManager
from sqlalchemy.orm.session import Session


class DataRecorderService:
    @staticmethod
    def get_processed_dir_path(machine_id: str, started_at: datetime) -> str:
        """処理済みファイルおよびpklファイル格納用のディレクトリ取得（なければ作成）"""

        jst_started_at: datetime = started_at + timedelta(hours=9)
        datetime_suffix: str = jst_started_at.strftime("%Y%m%d%H%M%S")

        dir_name: str = machine_id + "-" + datetime_suffix

        processed_dir_path: str = os.path.join(os.environ["data_dir"], dir_name)

        if os.path.isdir(processed_dir_path):
            logger.debug(f"{processed_dir_path} is already exists")
        else:
            os.makedirs(processed_dir_path)
            logger.info(f"{processed_dir_path} created.")

        return processed_dir_path

    @staticmethod
    def record(db: Session, machine_id: str) -> None:
        """バイナリデータをpklに変換して出力する。celeryタスクから実行。"""

        logger.info(f"data recording process started. machine_id: {machine_id}")

        try:
            latest_data_collect_history: DataCollectHistory = CRUDDataCollectHistory.select_latest_by_machine_id(db, machine_id)
        except Exception:
            logger.exception(traceback.format_exc())
            sys.exit(1)

        sensors: List[DataCollectHistoryDetail] = latest_data_collect_history.data_collect_history_details
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

        started_timestamp: float = latest_data_collect_history.started_at.timestamp()

        num_of_records: int = 0
        INTERVAL: Final[int] = 1
        data_dir: str = os.environ["data_dir"]

        # データ収集が停止されるまで一定間隔で無限ループ実行。
        while True:
            time.sleep(INTERVAL)

            # NOTE: db sessionを使いまわすと更新データが取得できないため、新しいsessionを用意
            _db: Session = SessionLocal()
            machine: Machine = CRUDMachine.select_by_id(db, machine_id)
            collect_status: str = machine.collect_status
            _db.close()

            # collect_statusがRECORDEDになるのは、停止ボタン押下後全てのバイナリファイルが捌けたとき。
            if collect_status == common.COLLECT_STATUS.RECORDED.value:
                logger.info(f"data recording process stopped. machine_id: {machine_id}")
                break

            # 対象機器のファイルリストを作成
            files_info: List[FileInfo] = FileManager.create_files_info(data_dir, machine_id, "dat")

            # バイナリファイルが未生成のタイミングはあり得る（例えばネットワーク遅延等）
            if len(files_info) == 0:
                logger.debug(f"No files in {data_dir}")
                continue

            # NOTE: 生成中のファイルを読み込まないよう、安全バッファとして3秒待つ
            time.sleep(3)

            num_of_records = DataRecorderService.data_record(
                latest_data_collect_history,
                files_info,
                Decimal(started_timestamp),
                num_of_records,
                displacement_sensor_id,
                sensor_ids_other_than_displacement,
            )

    @staticmethod
    def data_record(
        data_collect_history: DataCollectHistory,
        target_files: List[FileInfo],
        started_timestamp: Decimal,
        num_of_records: int,
        displacement_sensor_id: str,
        sensor_ids_other_than_displacement: List[str],
        is_manual: bool = False,
    ) -> int:
        """バイナリファイル読み取りおよびES/pkl出力"""

        sequential_number: int = num_of_records
        # プロセス跨ぎを考慮した時刻付け
        sampling_interval: Decimal = Decimal(1.0 / data_collect_history.sampling_frequency)
        timestamp: Decimal = started_timestamp + sequential_number * sampling_interval

        for file in target_files:
            # バイナリファイルを読み取り、データリストを取得
            samples: List[Dict[str, Any]]
            samples, sequential_number, timestamp = DataRecorderService.read_binary_files(
                file,
                sequential_number,
                timestamp,
                data_collect_history,
                displacement_sensor_id,
                sensor_ids_other_than_displacement,
                sampling_interval,
            )

            # pklファイルに出力
            FileManager.export_to_pickle(samples, file, data_collect_history.processed_dir_path)

            # 手動インポートでないとき（スケジュール実行のとき）、ファイルを退避する
            if not is_manual:
                shutil.move(file.file_path, data_collect_history.processed_dir_path)

            logger.info(f"processed: {file.file_path}, sequential_number(count): {sequential_number}")

        # 記録した件数
        return sequential_number

    @staticmethod
    def read_binary_files(
        file: FileInfo,
        sequential_number: int,
        timestamp: Decimal,
        data_collect_history: DataCollectHistory,
        displacement_sensor_id: str,
        sensor_ids_other_than_displacement: List[str],
        sampling_interval: Decimal,
    ) -> Tuple[List[Dict[str, Any]], int, Decimal]:
        """バイナリファイルを読んで、そのデータをリストにして返す"""

        BYTE_SIZE: Final[int] = 8
        ROUND_DIGITS: Final[int] = 3
        SAMPLING_CH_NUM: Final[int] = data_collect_history.sampling_ch_num
        ROW_BYTE_SIZE: Final[int] = BYTE_SIZE * SAMPLING_CH_NUM  # 8 byte * チャネル数
        UNPACK_FORMAT: Final[str] = "<" + "d" * SAMPLING_CH_NUM  # 5chの場合 "<ddddd"

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
                displacement_sensor_id: round(dataset[0], ROUND_DIGITS),
            }

            # 変位センサー以外のセンサー
            for i, s in enumerate(sensor_ids_other_than_displacement):
                sample[s] = round(dataset[i + 1], ROUND_DIGITS)

            samples.append(sample)

            dataset_number += 1
            sequential_number += 1

            # NOTE: 100kサンプリングの場合10μ秒(=0.00001秒=1e-5秒)
            timestamp += sampling_interval

        return samples, sequential_number, timestamp
