import dataclasses
import glob
import os
import re
import sys
import time
from datetime import datetime
from typing import Final, List

import pandas as pd
from backend.app.models.data_collect_history_handler import DataCollectHistoryHandler
from backend.common.common_logger import logger
from pandas.core.frame import DataFrame


@dataclasses.dataclass
class FileInfo:
    __slots__ = (
        "file_path",
        "timestamp",
    )
    file_path: str
    timestamp: float


class FileManager:
    @staticmethod
    def create_files_info(target_dir: str, machine_id: str, gateway_id: str, handler_id: str, extension: str) -> List[FileInfo]:
        """指定した拡張子ファイルの情報（パスとファイル名から抽出した日時）リストを生成"""

        file_list: List[str] = glob.glob(os.path.join(target_dir, f"{machine_id}_{gateway_id}_{handler_id}_*.{extension}"))

        if len(file_list) == 0:
            return []

        file_list.sort()

        # ファイルリストから時刻データを生成
        files_timestamp: map[float] = map(FileManager._create_file_timestamp, file_list)
        # リストを作成 [{"file_path": "xxx", "timestamp": "yyy"},...]
        files_info: List[FileInfo] = [FileInfo(file_path=row[0], timestamp=row[1]) for row in zip(file_list, files_timestamp)]

        return files_info

    @staticmethod
    def get_files_info(machine_id: str, gateway_id: str, handler_id: str, target_date_str: str) -> List[FileInfo]:
        target_dir = machine_id + "-" + target_date_str
        data_dir: str = os.environ["data_dir"]
        data_full_path: str = os.path.join(data_dir, target_dir)

        files_info: List[FileInfo] = FileManager.create_files_info(data_full_path, machine_id, gateway_id, handler_id, "pkl")

        return files_info

    @staticmethod
    def get_files_info_by_handler(machine_id: str, target_date_str: str, handlers: List[DataCollectHistoryHandler]) -> List[List[FileInfo]]:
        """ハンドラー毎のファイル情報を取得する"""

        files_info_by_handler: List[List[FileInfo]] = []
        for handler in handlers:
            files_info: List[FileInfo] = FileManager.get_files_info(
                machine_id, handler.data_collect_history_gateway.gateway_id, handler.handler_id, target_date_str
            )
            if len(files_info) == 0:
                raise Exception

            files_info_by_handler.append(files_info)

        return files_info_by_handler

    @staticmethod
    def get_num_of_files_unified_handler(files_info_by_handler: List[List[FileInfo]]) -> int:
        """ハンドラー毎のファイル数をチェックし、その数を返す。この数はハンドラー毎に同じであるはずだが、一致しない場合は最小ファイル数を返す。"""

        files_len_list = []
        for files_info in files_info_by_handler:
            files_len_list.append(len(files_info))

        # ハンドラーごとでファイル数は一致するはずだが、もし一致しない場合は最小値を返す。
        if not all(val == files_len_list[0] for val in files_len_list):
            logger.error("The number of files for each handler does not match.")
            return min(files_len_list)

        return files_len_list[0]

    @staticmethod
    def _create_file_timestamp(filepath: str) -> float:
        """ファイル名から日時データを作成する。
        ファイル名は 機器名_AD-XX_YYYYmmddHHMMSS.ffffff 形式が前提となる。
        """

        filename: str = os.path.basename(filepath)

        parts: List[str] = re.findall(r"\d+", filename)
        timestamp_str: str = parts[-3] + parts[-2] + parts[-1]
        timestamp: float = datetime.strptime(timestamp_str, "%Y%m%d%H%M%S%f").timestamp()

        return timestamp

    @staticmethod
    def get_target_files(files_info: List[FileInfo], start_time: float, end_time: float) -> List[FileInfo]:
        """処理対象(開始/終了区間に含まれる）ファイルリストを返す"""

        return list(filter(lambda x: start_time <= x.timestamp <= end_time, files_info))

    @staticmethod
    def get_not_target_files(files_info: List[FileInfo], start_time: float, end_time: float) -> List[FileInfo]:
        """処理対象外(開始/終了区間に含まれない）ファイルリストを返す"""

        return list(filter(lambda x: (x.timestamp < start_time or x.timestamp > end_time), files_info))

    @staticmethod
    def export_to_pickle(samples: List[dict], file: FileInfo, processed_dir_path: str) -> None:
        """pickleファイルに出力する"""

        df: DataFrame = pd.DataFrame(samples)

        pickle_filename: str = os.path.splitext(os.path.basename(file.file_path))[0]
        pickle_filepath: str = os.path.join(processed_dir_path, pickle_filename) + ".pkl"
        df.to_pickle(pickle_filepath)

    @staticmethod
    def get_files(dir_path: str, pattern: str) -> List[str]:
        """指定したディレクトリから、指定した形式のファイル名に一致するファイル名リストを取得する"""

        files: List[str] = glob.glob(os.path.join(dir_path, pattern))
        files.sort()

        return files

    @staticmethod
    def get_pickle_file_list(machine_id: str, rawdata_dir_path: str, handlers) -> List[List[str]]:
        """pickleファイルリストを取得する。
        複数ハンドラーの場合、pklファイルをファイルセット(1つのリストに全ADCの1ファイル分）のリストにまとめて返す
        ex: ADC3台の場合
        [[ADC1_1.pkl, ADC2_1.pkl, ADC3_1.pkl], [ADC1_2.pkl, ADC2_2.pkl, ADC3_2.pkl], ...]
        """

        MAX_RETRY_COUNT: Final[int] = 3
        RETRY_INTERVAL: Final[int] = 3
        retry_count = 0

        while True:
            if retry_count == MAX_RETRY_COUNT:
                logger.error("Each handlers have diffent number of files.")
                sys.exit(1)

            # 取り込むpickleファイルのリストをまずはハンドラー関係なく取得。
            all_pickle_files: List[str] = FileManager.get_files(dir_path=rawdata_dir_path, pattern=f"{machine_id}_*.pkl")
            if len(all_pickle_files) == 0:
                time.sleep(RETRY_INTERVAL)
                continue

            pickle_files_by_handler: List[List[str]] = []  # [[ADC1_1, ADC1_2, ADC1_3, ...], [ADC2_1, ADC2_2, ADC2_3, ...], ...]
            for i, handler in enumerate(handlers):
                pickle_files_in_handler: List[str] = [s for s in all_pickle_files if handler.handler_id in s]
                # 最初のハンドラーのファイル数を基準とする。
                if i == 0:
                    tmp_len: int = len(pickle_files_in_handler)
                # 2つめのハンドラー以降は、最初のハンドラーのファイル数と一致していること。一致しなければbreakして全pickleファイル再取得。
                else:
                    if len(pickle_files_in_handler) != tmp_len:
                        retry_count += 1
                        break
                pickle_files_by_handler.append(pickle_files_in_handler)

            if len(pickle_files_by_handler) == len(handlers):
                logger.info("All handler has same number of files.")
                break

            time.sleep(RETRY_INTERVAL)

        file_set_list = []  # [[ADC1_1, ADC2_1, ADC3_1], [ADC1_2, ADC2_2, ADC3_2], ...]
        for file_number in range(len(pickle_files_by_handler[0])):
            file_set = [x[file_number] for x in pickle_files_by_handler]
            file_set_list.append(file_set)

        return file_set_list

    @staticmethod
    def get_files_list(machine_id, handlers: List[DataCollectHistoryHandler], rawdata_dir_path: str) -> List[List[str]]:
        """ショット切り出し対象ファイルリストを返す。ハンドラーが単一か複数台かで分岐。"""

        # 単一ハンドラー
        if len(handlers) == 1:
            files: List[str] = FileManager.get_files(dir_path=rawdata_dir_path, pattern=f"{machine_id}_*.pkl")
            files_list: List[List[str]] = [[x] for x in files]
        # 複数ハンドラー
        else:
            files_list = FileManager.get_pickle_file_list(machine_id, rawdata_dir_path, handlers)

        return files_list
