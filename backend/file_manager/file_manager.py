import os
import re
import glob
import dataclasses
import pandas as pd
from pandas.core.frame import DataFrame
from datetime import datetime
from typing import List, Optional


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
    def create_files_info(target_dir: str, machine_id: str, extension: str) -> Optional[List[FileInfo]]:
        """指定した拡張子ファイルの情報（パスとファイル名から抽出した日時）リストを生成"""

        file_list: List[str] = glob.glob(os.path.join(target_dir, f"{machine_id}_*.{extension}"))

        if len(file_list) == 0:
            return None

        file_list.sort()

        # ファイルリストから時刻データを生成
        files_timestamp: map[float] = map(FileManager._create_file_timestamp, file_list)
        # リストを作成 [{"file_path": "xxx", "timestamp": "yyy"},...]
        files_info: List[FileInfo] = [
            FileInfo(file_path=row[0], timestamp=row[1]) for row in zip(file_list, files_timestamp)
        ]

        return files_info

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
