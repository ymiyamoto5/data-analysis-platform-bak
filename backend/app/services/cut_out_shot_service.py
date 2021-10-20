import os
from datetime import datetime
from typing import List, Optional

import pandas as pd
from backend.app.models.sensor import Sensor
from backend.common import common
from backend.data_converter.data_converter import DataConverter
from backend.file_manager.file_manager import FileInfo, FileManager
from pandas.core.frame import DataFrame


class CutOutShotService:
    @staticmethod
    def get_target_dir(target_date_timestamp: str) -> str:
        """ブラウザから文字列で渡されたUNIXTIME(ミリ秒単位）から、データディレクトリ名の日付文字列を特定して返却"""

        # NOTE: ブラウザからは文字列のUNIXTIME(ミリ秒)で与えられる。秒単位に直して変換。
        target_date: datetime = datetime.fromtimestamp(int(target_date_timestamp) / 1000)
        target_date_str: str = datetime.strftime(target_date, "%Y%m%d%H%M%S")

        return target_date_str

    @staticmethod
    def get_files_info(machine_id: str, target_date_str: str) -> Optional[List[FileInfo]]:
        target_dir = machine_id + "-" + target_date_str
        data_dir: Optional[str] = os.getenv("data_dir")
        data_full_path: str = os.path.join(data_dir, target_dir)

        files_info: Optional[List[FileInfo]] = FileManager.create_files_info(data_full_path, machine_id, "pkl")

        return files_info

    @staticmethod
    def fetch_df(target_file: str) -> DataFrame:
        """引数で指定したファイル名のpklファイルを読み込みDataFrameで返す"""

        df = pd.read_pickle(target_file)

        return df

    @staticmethod
    def resample_df(df: DataFrame, sampling_frequency: int, rate: int) -> DataFrame:
        """引数のDataFrameについてリサンプリングして返却する"""

        df = DataConverter.down_sampling_df(df, sampling_frequency, rate=rate)

        return df

    @staticmethod
    def physical_convert_df(df: DataFrame, sensors: List[Sensor]) -> DataFrame:
        """引数のDataFrameをリサンプリングして返却する"""

        for sensor in sensors:
            func = DataConverter.get_physical_conversion_formula(sensor)
            df.loc[:, sensor.sensor_id] = df[sensor.sensor_id].map(func)

        return df
