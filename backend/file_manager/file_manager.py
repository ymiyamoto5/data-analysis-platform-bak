import dataclasses
import glob
import os
import re
from datetime import datetime
from typing import List

import pandas as pd
from backend.app.models.data_collect_history_handler import DataCollectHistoryHandler
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
        """指定した機器、GW、ハンドラー、拡張子ファイルの情報（パスとファイル名から抽出した日時）リストを生成"""

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
    def create_files_info_by_machine_id(target_dir: str, machine_id: str, extension: str) -> List[FileInfo]:
        """指定した機器、拡張子ファイルの情報（パスとファイル名から抽出した日時）リストを生成（manual_recordで利用）"""

        file_list: List[str] = glob.glob(os.path.join(target_dir, f"{machine_id}_*.{extension}"))

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
        target_dir = machine_id + "_" + target_date_str
        data_dir: str = os.environ["DATA_DIR"]
        data_full_path: str = os.path.join(data_dir, target_dir)

        files_info: List[FileInfo] = FileManager.create_files_info(data_full_path, machine_id, gateway_id, handler_id, "pkl")

        return files_info

    @staticmethod
    def _create_file_timestamp(filepath: str) -> float:
        """ファイル名から日時データを作成する。
        ファイル名は{machine_id}_{gateway_id}_{handler_id}_{YYYYmmdd}-{HHMMSS}.{ffffff}_{file_number}.dat 形式が前提となる。
        """

        filename: str = os.path.basename(filepath)

        parts: List[str] = re.findall(r"\d+", filename)
        # NOTE: ファイル名の形式決め打ち実装なので注意
        timestamp_str = parts[-4] + parts[-3] + parts[-2]
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
