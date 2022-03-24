import os
from datetime import datetime
from typing import Tuple

from backend.common import common
from backend.data_reader.data_reader import DataReader
from backend.utils.df_to_els import df_to_els  # type: ignore
from pandas.core.frame import DataFrame


def resampling(shots_df: DataFrame, resampling_rate: int, exclude_shots: Tuple[int, ...]):
    """指定したrateでリサンプリング"""

    print("resampling start...")

    return shots_df[shots_df.sequential_number_by_shot % resampling_rate == 0].reset_index(drop=True)


def convert_timestamp(df: DataFrame):
    """unixtimeをdatetimeに変換"""

    # def format_time(x: float) -> datetime:
    #     _x = round(x, 3)
    #     return datetime.fromtimestamp(_x)

    timestamp_to_datetime = lambda x: datetime.fromtimestamp(x)
    df.timestamp = df.timestamp.apply(timestamp_to_datetime)
    # truncate_micro_seconds = lambda x: round(x, 3)
    # df.timestamp = df.timestamp.apply(truncate_micro_seconds)
    # df.timestamp = df.timestamp.apply(format_time)
    return df


if __name__ == "__main__":
    target = "20210327141514"
    shots_data_index = "shots-" + target + "-data"
    shots_meta_index = "shots-" + target + "-meta"
    resample_index = "shots-" + target + "-resample"

    dr = DataReader()
    shots_df: DataFrame = dr.multi_process_read_all(shots_data_index)
    # shots_df: DataFrame = dr.read_shot(shots_data_index, 10)
    shots_meta_df = dr.read_shots_meta(shots_meta_index)

    exclude_shots = (983, 1227, 1228, 1229, 1369, 1381)

    resample_df = resampling(shots_df, 100, exclude_shots)
    # converted_df = convert_timestamp(resample_df)

    setting: str = os.environ["SETTING_RESAMPLE_PATH"]

    df_to_els(resample_df, resample_index, mapping=None, setting=setting)

    print("resampling end")
