"""
 ==================================
  data_recorder.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import multiprocessing
import os
import sys
import glob
import re
import shutil
import struct
import time
import traceback
import pandas as pd
from datetime import datetime
from pandas.core.frame import DataFrame
from typing import Final, Tuple, List, Optional, Any
import dataclasses
import argparse
from backend.elastic_manager.elastic_manager import ElasticManager
from backend.event_manager.event_manager import EventManager
from backend.common import common
from backend.common.dao.machine_dao import MachineDAO
from backend.common.dao.handler_dao import HandlerDAO
from backend.data_collect_manager.models.machine import Machine
from backend.data_collect_manager.models.handler import Handler
from backend.common.common_logger import data_recorder_logger as logger


@dataclasses.dataclass
class FileInfo:
    __slots__ = (
        "file_path",
        "timestamp",
    )
    file_path: str
    timestamp: float


class DataRecorder:
    def __init__(self, machine_id: str, handler: Handler = None):
        self.machine_id: str = machine_id

        if handler is None:
            try:
                handler = HandlerDAO.fetch_handler(self.machine_id)
            except Exception:
                logger.exception(traceback.format_exc())
                sys.exit(1)

        self.sampling_ch_num: int = handler.sampling_ch_num
        self.sampling_frequency: int = handler.sampling_frequency
        self.sampling_interval: float = 1.0 / self.sampling_frequency

    @staticmethod
    def _create_file_timestamp(filepath: str) -> float:
        """ファイル名から日時データを作成する。
        ファイル名は AD-XX_YYYYmmddHHMMSS.ffffff 形式が前提となる。
        """

        filename: str = os.path.basename(filepath)

        parts: List[str] = re.findall(r"\d+", filename)
        timestamp_str: str = parts[-3] + parts[-2] + parts[-1]
        timestamp: float = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S%f").timestamp()

        return timestamp

    @staticmethod
    def _get_target_interval(events: List[dict]) -> Tuple[float, float]:
        """処理対象となる区間（開始/終了時刻）を取得する"""

        start_time: Optional[float] = EventManager.get_collect_setup_time(events)

        if start_time is None:
            sys.exit(1)

        end_time: float = EventManager.get_collect_end_time(events)

        if end_time == common.TIMESTAMP_MAX:
            logger.info(f"target interval: {datetime.fromtimestamp(start_time)} - ")
        else:
            logger.info(f"target interval: {datetime.fromtimestamp(start_time)} - {datetime.fromtimestamp(end_time)}")

        return start_time, end_time

    @staticmethod
    def _get_target_files(files_info: List[FileInfo], start_time: float, end_time: float) -> List[FileInfo]:
        """処理対象(開始/終了区間に含まれる）ファイルリストを返す"""

        return list(filter(lambda x: start_time <= x.timestamp <= end_time, files_info))

    @staticmethod
    def _get_not_target_files(files_info: List[FileInfo], start_time: float, end_time: float) -> List[FileInfo]:
        """処理対象外(開始/終了区間に含まれない）ファイルリストを返す"""

        return list(filter(lambda x: (x.timestamp < start_time or x.timestamp > end_time), files_info))

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

            sample: dict = {
                "sequential_number": sequential_number,
                "timestamp": timestamp,
                "displacement": round(dataset[0], 3),
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

    def _create_files_info(self, data_dir: str) -> Optional[List[FileInfo]]:
        """バイナリファイルの情報（パスとファイル名から抽出した日時）リストを生成"""

        file_list: List[str] = glob.glob(os.path.join(data_dir, f"{self.machine_id}_*.dat"))

        if len(file_list) == 0:
            return None

        file_list.sort()

        # ファイルリストから時刻データを生成
        files_timestamp: map[float] = map(self._create_file_timestamp, file_list)
        # リストを作成 [{"file_path": "xxx", "timestamp": "yyy"},...]
        files_info: List[FileInfo] = [
            FileInfo(file_path=row[0], timestamp=row[1]) for row in zip(file_list, files_timestamp)
        ]

        return files_info

    @staticmethod
    def _export_to_pickle(samples: List[dict], file: FileInfo, processed_dir_path: str) -> None:
        """pickleファイルに出力する"""

        df: DataFrame = pd.DataFrame(samples)

        pickle_filename: str = os.path.splitext(os.path.basename(file.file_path))[0]
        pickle_filepath: str = os.path.join(processed_dir_path, pickle_filename) + ".pkl"
        df.to_pickle(pickle_filepath)

    def _set_timestamp(self, rawdata_index: str, started_timestamp: float) -> float:
        """プロセス跨ぎのタイムスタンプ設定。
        rawdataインデックスの最新データから取得（なければデータ収集開始時間）
        """

        query: dict = {"sort": {"sequential_number": {"order": "desc"}}}
        latest_rawdata: List[dict] = ElasticManager.get_docs(index=rawdata_index, query=query, size=1)

        timestamp: float = (
            started_timestamp if len(latest_rawdata) == 0 else latest_rawdata[0]["timestamp"] + self.sampling_interval
        )

        return timestamp

    def _data_record(
        self,
        rawdata_index: str,
        target_files: List[FileInfo],
        processed_dir_path: str,
        started_timestamp: float,
        is_manual: bool = False,
    ) -> None:
        """バイナリファイル読み取りおよびES/pkl出力"""

        sequential_number: int = ElasticManager.count(rawdata_index)  # ファイル（プロセス）を跨いだ連番
        timestamp: float = self._set_timestamp(rawdata_index, started_timestamp)

        logger.debug(
            f"sequential_number(count):{sequential_number}, started:{started_timestamp}, timestamp:{timestamp}"
        )

        procs: List[multiprocessing.context.Process] = []

        for file in target_files:
            # バイナリファイルを読み取り、データリストを取得
            samples: List[dict]
            sequential_number
            samples, sequential_number, timestamp = self._read_binary_files(file, sequential_number, timestamp)

            if len(procs) > 0:
                for p in procs:
                    p.join()

            procs = ElasticManager.multi_process_bulk_lazy_join(
                data=samples, index_to_import=rawdata_index, num_of_process=common.NUM_OF_PROCESS, chunk_size=5000
            )

            self._export_to_pickle(samples, file, processed_dir_path)

            # 手動インポートでないとき（スケジュール実行のとき）、ファイルを退避する
            if not is_manual:
                shutil.move(file.file_path, processed_dir_path)

            logger.info(f"processed: {file.file_path}")

        if len(procs) > 0:
            for p in procs:
                p.join()

    def auto_record(self, is_debug_mode: bool = False) -> None:
        """スケジュール実行による自動インポート"""

        # データディレクトリを確認し、対象機器のファイルリストを作成
        data_dir: str = common.get_config_value(common.APP_CONFIG_PATH, "data_dir")
        files_info: Optional[List[FileInfo]] = self._create_files_info(data_dir)

        if files_info is None:
            logger.info(f"No files in {data_dir}")
            return

        # 対象機器について、直近のevents_indexからイベント取得
        latest_events_index: Optional[str] = EventManager.get_latest_events_index(self.machine_id)

        if latest_events_index is None:
            logger.error("events_index is not found.")
            return

        datetime_str: str = latest_events_index.split("-")[-1]  # YYYYmmddHHMMSS文字列
        suffix: str = self.machine_id + "-" + datetime_str
        events_index: str = "events-" + suffix
        events: List[dict] = EventManager.fetch_events(events_index)

        if len(events) == 0:
            logger.error("Exits because no events.")
            return

        # 最後のイベントがrecordedの場合、前回のデータ採取＆記録完了から状態が変わっていないので、何もしない
        if events[-1]["event_type"] == common.COLLECT_STATUS.RECORDED.value:
            logger.info(
                f"Exits because the latest event is '{common.COLLECT_STATUS.RECORDED.value}'. May be data collect has not started yet."
            )
            return

        started_timestamp: float = datetime.fromisoformat(events[0]["occurred_time"]).timestamp()

        start_time: float
        end_time: float
        start_time, end_time = self._get_target_interval(events)

        # 対象となるファイルに絞り込む
        target_files: List[FileInfo] = self._get_target_files(files_info, start_time, end_time)

        # 含まれないファイルは削除するが、debug_modeでは削除しない
        if not is_debug_mode:
            not_target_files: List[FileInfo] = self._get_not_target_files(files_info, start_time, end_time)
            for file in not_target_files:
                os.remove(file.file_path)
                logger.info(f"{file.file_path} has been deleted because it is out of range.")

        if len(target_files) == 0:
            logger.info("No files in target inteverl")
            return

        logger.info(f"{len(target_files)} / {len(files_info)} files are target.")

        # 処理済みファイルおよびテンポラリファイル格納用のディレクトリ作成
        processed_dir_path: str = os.path.join(data_dir, suffix)
        if os.path.isdir(processed_dir_path):
            logger.debug(f"{processed_dir_path} is already exists")
        else:
            os.makedirs(processed_dir_path)
            logger.info(f"{processed_dir_path} created.")

        # Elasticsearch rawdataインデックス名
        rawdata_index: str = "rawdata-" + suffix

        # start_timeが変わらない（格納先が変わらない）限り、同一インデックスにデータを追記していく
        if not ElasticManager.exists_index(rawdata_index):
            logger.info(f"{rawdata_index} not exists. Creating...")
            mapping_file: str = common.get_config_value(common.APP_CONFIG_PATH, "mapping_rawdata_path")
            setting_file: str = common.get_config_value(common.APP_CONFIG_PATH, "setting_rawdata_path")
            ElasticManager.create_index(rawdata_index, mapping_file, setting_file)

        # NOTE: 生成中のファイルを読み込まないよう、安全バッファとして3秒待つ
        time.sleep(3)

        self._data_record(rawdata_index, target_files, processed_dir_path, started_timestamp)

        logger.info("all file processed.")

    def manual_record(self, target_dir: str):
        """手動での生データ取り込み。前提条件は以下。
        * 取り込むデータディレクトリはdataフォルダ配下に配置すること。
        * 対応するevents_indexが存在すること。
        * 対応するevents_indexの最後のドキュメントがrecordedであること。
        """

        files_info: Optional[List[FileInfo]] = self._create_files_info(target_dir)

        if files_info is None:
            logger.info(f"No files in {target_dir}")
            return

        events_index: str = "events-" + os.path.basename(os.path.dirname(target_dir))
        events: List[dict] = EventManager.fetch_events(events_index)

        if len(events) == 0:
            logger.error("Exits because no events.")
            return

        # 直近のイベントがrecordedでない（データ収集が完了していない）場合は、手動実行させない。
        if events[-1]["event_type"] != common.COLLECT_STATUS.RECORDED.value:
            logger.error(f"Latest event should be '{common.COLLECT_STATUS.RECORDED.value}'.")
            return

        started_timestamp: float = datetime.fromisoformat(events[0]["occurred_time"]).timestamp()

        rawdata_dir_name: str = os.path.basename(target_dir)
        rawdata_index: str = "rawdata-" + self.machine_id + "-" + rawdata_dir_name

        # インデックスが存在すれば再作成
        ElasticManager.delete_exists_index(index=rawdata_index)
        mapping_file: str = common.get_config_value(common.APP_CONFIG_PATH, "mapping_rawdata_path")
        setting_file: str = common.get_config_value(common.APP_CONFIG_PATH, "setting_rawdata_path")
        ElasticManager.create_index(rawdata_index, mapping_file, setting_file)

        self._data_record(rawdata_index, files_info, target_dir, started_timestamp, is_manual=True)

        logger.info("manual import finished.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", help="set import directory (manual import)")
    parser.add_argument("--debug", action="store_true", help="debug mode")
    args = parser.parse_args()

    machines: List[Machine] = MachineDAO.select_machines_has_handler()

    # スケジュール実行
    if args.dir is None:
        for m in machines:
            data_recorder = DataRecorder(m.machine_id)
            data_recorder.auto_record(args.debug)

    # 手動インポート
    else:
        data_dir: str = common.get_config_value(common.APP_CONFIG_PATH, "data_dir")
        target_dir: str = os.path.join(data_dir, args.dir)

        if not os.path.isdir(target_dir):
            logger.error(f"{args.dir} is not exists.")
            sys.exit(1)

        # TODO: 変数化
        machine_id = "machine-01"
        data_recorder = DataRecorder(machine_id)
        data_recorder.manual_record(target_dir)
