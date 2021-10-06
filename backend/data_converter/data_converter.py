from datetime import datetime
from typing import Callable

from backend.app.models.sensor import Sensor
from backend.common.common_logger import logger
from pandas.core.frame import DataFrame


class DataConverter:
    @staticmethod
    def get_physical_conversion_formula(sensor: Sensor) -> Callable[[float], float]:
        """センサー種別に応じた物理変換式を返却する"""

        if sensor.sensor_type_id == "load":
            base_volt: float = sensor.base_volt
            base_load: float = sensor.base_load

            return lambda v: base_load / base_volt * v

        elif sensor.sensor_type_id == "volt":
            base_volt = sensor.base_volt
            base_load = sensor.base_load
            initial_volt: float = sensor.initial_volt

            return lambda v: base_load * (v - initial_volt) / (base_volt - initial_volt)

        elif sensor.sensor_type_id == "displacement":
            return lambda v: 70.0 - (v - 2.0) * 70.0 / 8.0

        elif sensor.sensor_type_id == "pulse":
            return lambda v: v

        else:
            return lambda v: v

    @staticmethod
    def down_sampling_df(df: DataFrame, sampling_frequency: int, rate: int) -> DataFrame:
        """データ収集時のサンプリング間隔を元に、rate倍のダウンサンプリングする
        ex) 元のsampling_frequency=100,000(間隔10μs) をrate=1,000(倍)ダウンサンプリング --> リサンプリング間隔100ms
            元のsampling_frequency=1,000(間隔1ms) をrate=1,000(倍)ダウンサンプリング --> リサンプリング間隔1s
        """

        # rate < 1、つまりアップサンプリングは許可しない
        if rate < 1:
            logger.error(f"Invalid parameter 'rate'={rate}. 'n' should be greater than 1.")
            return df

        # timestampを日時に戻しdaterange indexとする。
        df["timestamp"] = df["timestamp"].map(lambda x: datetime.fromtimestamp(x))
        df = df.set_index(["timestamp"])

        sampling_interval: float = 1 / sampling_frequency
        resampling_interval: float = sampling_interval * rate

        # ミリ秒未満、例えば10μ秒⇒1μ秒等のリサンプリングは対応しない。最も粒度の細かい1ms秒に強制する。
        if resampling_interval < 1e-3:
            logger.warn(f"Invalid resampling_interval={resampling_interval}.")
            resampling_interval_str = "1ms"
        elif resampling_interval < 1:
            resampling_interval_str = str(int(resampling_interval * 1000)) + "ms"
        else:
            resampling_interval_str = str(int(resampling_interval)) + "s"

        df = df.resample(resampling_interval_str).mean()
        df = df.reset_index()

        return df
