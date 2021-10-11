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
import shutil
import struct
import sys
import time
import traceback
from datetime import datetime
from typing import Any, Dict, Final, List, Optional, Tuple

import requests
from backend.common import common
from backend.common.common_logger import data_recorder_logger as logger
from backend.file_manager.file_manager import FileInfo, FileManager

API_URL: Final[str] = common.get_config_value(common.APP_CONFIG_PATH, "API_URL")


class DataRecorder:
    def __init__(self, machine_id: str):
        self.machine_id: str = machine_id

        try:
            response = requests.get(API_URL + f"/machines/{machine_id}/handler")
            handler: Dict[str, Any] = response.json()
        except Exception:
            logger.exception(traceback.format_exc())
            sys.exit(1)

        self.sampling_ch_num: int = handler["sampling_ch_num"]
        self.sampling_frequency: int = handler["sampling_frequency"]
        self.sampling_interval: float = 1.0 / self.sampling_frequency

    def _set_timestamp(self, sample_count: int, started_timestamp: float) -> float:
        """プロセス跨ぎのタイムスタンプ設定。"""

        timestamp: float = (
            started_timestamp if sample_count == 0 else started_timestamp + sample_count * self.sampling_interval
        )

        return timestamp

    def _read_binary_files(
        self, file: FileInfo, sequential_number: int, timestamp: float
    ) -> Tuple[List[dict], int, float]:
        """バイナリファイルを読んで、そのデータをリストにして返す"""

        BYTE_SIZE: Final[int] = 8
        ROW_BYTE_SIZE: Final[int] = BYTE_SIZE * self.sampling_ch_num  # 8 byte * チャネル数
        UNPACK_FORMAT: Final[str] = "<" + "d" * self.sampling_ch_num  # 5chの場合 "<ddddd"

        dataset_number: int = 0  # ファイル内での連番
        samples: List[dict] = []

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

            # TODO: pluseへの対応
            sample: dict = {
                "sequential_number": sequential_number,
                "timestamp": timestamp,
                "stroke_displacement": round(dataset[0], 3),
            }

            # 荷重センサーの数だけdictに追加
            for ch in range(1, self.sampling_ch_num):
                str_ch = str(ch).zfill(2)
                load: str = "load" + str_ch
                sample[load] = round(dataset[ch], 3)

            samples.append(sample)

            dataset_number += 1
            sequential_number += 1

            # NOTE: 100kサンプリングの場合10μ秒(=0.00001秒=1e-5秒)
            timestamp += self.sampling_interval

        return samples, sequential_number, timestamp

    def _data_record(
        self,
        latest_history_id: int,
        target_files: List[FileInfo],
        processed_dir_path: str,
        started_timestamp: float,
        sample_count: int,
        is_manual: bool = False,
    ) -> None:
        """バイナリファイル読み取りおよびES/pkl出力"""

        sequential_number: int = sample_count

        timestamp: float = self._set_timestamp(sample_count, started_timestamp)

        logger.debug(f"sequential_number(count):{sample_count}, started:{started_timestamp}, timestamp:{timestamp}")

        for file in target_files:
            # バイナリファイルを読み取り、データリストを取得
            samples: List[dict]
            samples, sequential_number, timestamp = self._read_binary_files(file, sequential_number, timestamp)

            try:
                requests.put(
                    API_URL + f"/data_collect_histories/{latest_history_id}/", json={"sample_count": sequential_number}
                )
            except Exception:
                logger.exception(traceback.format_exc())
                sys.exit(1)

            # pklファイルに出力
            FileManager.export_to_pickle(samples, file, processed_dir_path)

            # 手動インポートでないとき（スケジュール実行のとき）、ファイルを退避する
            if not is_manual:
                shutil.move(file.file_path, processed_dir_path)

            logger.info(f"processed: {file.file_path}")

    def auto_record(self, is_debug_mode: bool = False) -> None:
        """スケジュール実行による自動インポート"""

        # 対象機器のファイルリストを作成
        data_dir: str = common.get_config_value(common.APP_CONFIG_PATH, "data_dir")
        files_info: Optional[List[FileInfo]] = FileManager.create_files_info(data_dir, self.machine_id, "dat")

        if files_info is None:
            logger.info(f"No files in {data_dir}")
            return

        try:
            response = requests.get(API_URL + f"/data_collect_histories/{machine_id}/latest")
            latest_data_collect_history: Dict[str, Any] = response.json()
        except Exception:
            logger.exception(traceback.format_exc())
            sys.exit(1)

        events: List[Dict[str, Any]] = latest_data_collect_history["data_collect_history_events"]

        if len(events) == 0:
            logger.error("Exits because no events.")
            return

        # 最後のイベントがrecordedの場合、前回のデータ採取＆記録完了から状態が変わっていないので、何もしない
        if events[-1]["event_name"] == common.COLLECT_STATUS.RECORDED.value:
            logger.info(
                f"Exits because the latest event is '{common.COLLECT_STATUS.RECORDED.value}'. May be data collect has not started yet."
            )
            return

        started_at: str = latest_data_collect_history["started_at"]
        started_timestamp: float = datetime.fromisoformat(started_at).timestamp()
        ended_at: Optional[str] = latest_data_collect_history["ended_at"]
        if ended_at is not None:
            ended_timestamp: float = datetime.fromisoformat(ended_at).timestamp()
        else:
            ended_timestamp = common.TIMESTAMP_MAX

        # 対象となるファイルに絞り込む
        target_files: List[FileInfo] = FileManager.get_target_files(files_info, started_timestamp, ended_timestamp)

        # 含まれないファイルは削除するが、debug_modeでは削除しない
        if not is_debug_mode:
            not_target_files: List[FileInfo] = FileManager.get_not_target_files(
                files_info, started_timestamp, ended_timestamp
            )
            for file in not_target_files:
                os.remove(file.file_path)
                logger.info(f"{file.file_path} has been deleted because it is out of range.")

        if len(target_files) == 0:
            logger.info("No files in target interval")
            return

        logger.info(f"{len(target_files)} / {len(files_info)} files are target.")

        # 処理済みファイルおよびテンポラリファイル格納用のディレクトリ作成
        suffix: str = started_at
        processed_dir_path: str = os.path.join(data_dir, suffix)
        if os.path.isdir(processed_dir_path):
            logger.debug(f"{processed_dir_path} is already exists")
        else:
            os.makedirs(processed_dir_path)
            logger.info(f"{processed_dir_path} created.")

        # NOTE: 生成中のファイルを読み込まないよう、安全バッファとして3秒待つ
        time.sleep(3)

        sample_count: int = latest_data_collect_history["sample_count"]
        latest_history_id: int = latest_data_collect_history["id"]
        self._data_record(latest_history_id, target_files, processed_dir_path, started_timestamp, sample_count)

        logger.info("all file processed.")

    def manual_record(self, target_dir: str):
        """手動での生データ取り込み。前提条件は以下。
        * 取り込むデータディレクトリはdataフォルダ配下に配置すること。
        """

        files_info: Optional[List[FileInfo]] = FileManager.create_files_info(target_dir, self.machine_id, "dat")

        if files_info is None:
            logger.info(f"No files in {target_dir}")
            return

        try:
            response = requests.get(API_URL + f"/data_collect_histories/{machine_id}/latest")
            latest_data_collect_history: Dict[str, Any] = response.json()
            # sample_countを0に初期化する。
            latest_history_id: int = latest_data_collect_history["id"]
            requests.put(API_URL + f"/data_collect_histories/{latest_history_id}/", json={"sample_count": 0})
        except Exception:
            logger.exception(traceback.format_exc())
            sys.exit(1)

        events: List[Dict[str, Any]] = latest_data_collect_history["data_collect_history_events"]

        if len(events) == 0:
            logger.error("Exits because no events.")
            return

        # 直近のイベントがrecordedでない（データ収集が完了していない）場合は、手動実行させない。
        if events[-1]["event_name"] != common.COLLECT_STATUS.RECORDED.value:
            logger.error(f"Latest event should be '{common.COLLECT_STATUS.RECORDED.value}'.")
            return

        started_timestamp: float = datetime.fromisoformat(latest_data_collect_history["started_at"]).timestamp()
        sample_count: int = latest_data_collect_history["sample_count"]

        self._data_record(latest_history_id, files_info, target_dir, started_timestamp, sample_count, is_manual=True)

        logger.info("manual import finished.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", help="set import directory (manual import)")
    parser.add_argument("--debug", action="store_true", help="debug mode")
    args = parser.parse_args()

    os.environ["NO_PROXY"] = "localhost"
    response = requests.get(API_URL + "/machines/machines/has_handler")
    machines: List[Dict[str, Any]] = response.json()

    # スケジュール実行
    if args.dir is None:
        for m in machines:
            data_recorder = DataRecorder(m["machine_id"])
            data_recorder.auto_record(args.debug)

    # 手動インポート
    else:
        data_dir: str = common.get_config_value(common.APP_CONFIG_PATH, "data_dir")
        target_dir: str = os.path.join(data_dir, args.dir)

        if not os.path.isdir(target_dir):
            logger.error(f"{target_dir} is not exists.")
            sys.exit(1)

        machine_id = "-".join(args.dir.split("-")[:-1])
        data_recorder = DataRecorder(machine_id)
        data_recorder.manual_record(target_dir)
