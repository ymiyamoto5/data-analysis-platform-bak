import dataclasses
import glob
import os
import re
from datetime import datetime
from typing import List, Union

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
            files_info_by_handler.append(files_info)

        return files_info_by_handler

    @staticmethod
    def get_num_of_files_unified_handler(files_info_by_handler: Union[List[List[str]], List[List[FileInfo]]]) -> int:
        """ハンドラー毎のファイル数をチェックし、その数を返す。この数はハンドラー毎に同じであるはず。"""

        files_len_list = []
        for files_info in files_info_by_handler:
            files_len_list.append(len(files_info))

        # ハンドラーごとでファイル数は一致するはず
        if not all(val == files_len_list[0] for val in files_len_list):
            raise Exception("The number of files for each handler does not match.")

        return files_len_list[0]

    @staticmethod
    def _create_file_timestamp(filepath: str) -> float:
        """ファイル名から日時データを作成する。
        ファイル名は{machine_id}_{gateway_id}_{handler_id}_{YYYYmmdd}-{HHMMSS}.{ffffff}_{file_number}.dat 形式が前提となる。
        """

        filename: str = os.path.basename(filepath)

        parts: List[str] = re.findall(r"\d+", filename)
        # NOTE: ファイル名の形式決め打ち実装なので注意
        timestamp_str: str = parts[-4] + parts[-3] + parts[-2]
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

        # 取り込むpickleファイルのリストをまずはハンドラー関係なく取得。
        all_pickle_files: List[str] = FileManager.get_files(dir_path=rawdata_dir_path, pattern=f"{machine_id}_*.pkl")
        if len(all_pickle_files) == 0:
            return []

        # ハンドラー毎のリストを取得
        # [[ADC1_1, ADC1_2, ADC1_3, ...], [ADC2_1, ADC2_2, ADC2_3, ...], ...]
        pickle_files_by_handler: List[List[str]] = []
        for handler in handlers:
            # handler.id == "ADC1" のとき ["ADC1_1", "ADC1_2", "ADC1_3", ...]
            pickle_files_in_handler: List[str] = [s for s in all_pickle_files if handler.handler_id in s]
            pickle_files_by_handler.append(pickle_files_in_handler)

        # ファイルインデックス番号ごとのリストに変換
        try:
            file_set_list: List[List[str]] = FileManager.convert_to_file_set_list(pickle_files_by_handler)
        except Exception:
            raise
        if not FileManager.check_file_index_numbers_are_equal(file_set_list, ".pkl"):
            raise Exception("File index numbers are not equal by handler.")

        return file_set_list

    @staticmethod
    def check_file_index_numbers_are_equal(files_list: List[List[str]], extension: str) -> bool:
        """ファイル名サフィックスのインデックス番号をチェックし、ハンドラー毎に等しいことを確認する"""

        for files in files_list:
            for i, file_name in enumerate(files):
                # インデックス番号取得
                file_index_number: int = FileManager.get_file_index_number(file_name, extension)
                if i == 0:
                    compare_target: int = file_index_number
                    continue
                if file_index_number != compare_target:
                    return False

        return True

    @staticmethod
    def get_file_index_number(file_name: str, extension: str) -> int:
        """ファイル名サフィックスのインデックス番号を取得する"""

        file_name = file_name.replace(extension, "")
        return int(file_name.split("_")[-1])

    @staticmethod
    def convert_to_file_set_list(files_list: List[List[str]]) -> List[List[str]]:
        """リストを以下のように変換し、ファイルセットを得る。リスト要素の数はすべて等しいことが前提。
        [[ADC1_1, ADC1_2, ADC1_3, ...], [ADC2_1, ADC2_2, ADC2_3, ...], ...]
        --> [[ADC1_1, ADC2_1, ADC3_1, ...], [ADC1_2, ADC2_2, ADC3_2, ...], ...]
        """

        try:
            num_of_files: int = FileManager.get_num_of_files_unified_handler(files_list)
            # logger.info(f"num_of_files: {num_of_files}")
        except Exception:
            raise

        file_set_list = []
        for file_number in range(num_of_files):
            file_set = [x[file_number] for x in files_list]
            file_set_list.append(file_set)
        # logger.info(f"len(file_set_list): {len(file_set_list)}")

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
            try:
                files_list = FileManager.get_pickle_file_list(machine_id, rawdata_dir_path, handlers)
            except Exception:
                raise

        return files_list
