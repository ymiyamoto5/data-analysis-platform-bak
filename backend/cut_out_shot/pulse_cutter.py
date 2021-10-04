from typing import List

from backend.app.models.sensor import Sensor
from backend.common.common_logger import logger
from pandas.core.frame import DataFrame


class PulseCutter:
    def __init__(self, threshold: float):
        self.__threshold = threshold
        self.__shot_number: int = 0
        self.__sequential_number: int = 0
        self.__sequential_number_by_shot: int = 0
        self.__is_shot_section: bool = False  # ショット内か否かを判別する
        self.cut_out_targets: List[dict] = []
        self.shots_summary: List[dict] = []

    def set_sensors(self, sensors: List[Sensor]):
        self.__sensors = sensors

    def _detect_pulse_shot_start(self, pulse: float) -> bool:
        """ショット開始検知。ショットが未検出かつパルスがしきい値以上の場合、ショット開始とみなす。"""

        return (not self.__is_shot_section) and (pulse >= self.__threshold)

    def _detect_pulse_shot_end(self, pulse: float) -> bool:
        """ショット終了検知。ショットが検出されている状態かつパルスがしきい値を下回ったとき、ショット終了とみなす。"""

        return self.__is_shot_section and (pulse < self.__threshold)

    def _add_cut_out_target(self, rawdata) -> None:
        """切り出し対象としてデータを追加"""

        cut_out_target: dict = {
            "timestamp": rawdata.timestamp,
            "sequential_number": self.__sequential_number,
            "sequential_number_by_shot": self.__sequential_number_by_shot,
            "rawdata_sequential_number": int(rawdata.sequential_number),
            "shot_number": self.__shot_number,
            "tags": [],
        }

        for sensor in self.__sensors:
            cut_out_target[sensor.sensor_id] = getattr(rawdata, sensor.sensor_id)

        self.cut_out_targets.append(cut_out_target)

    def cut_out_shot(self, rawdata_df: DataFrame) -> None:
        """パルス信号によるショット切り出し
        パルス値がしきい値を超えたタイミングでショット区間開始
        以降、ループごとにパルス値を確認し、しきい値を下回っていたらショット区間終了
        """

        for rawdata in rawdata_df.itertuples():
            # pulseがしきい値以上のとき、ショットとして記録開始
            if self._detect_pulse_shot_start(rawdata.pulse):
                self.__is_shot_section = True  # ショット開始
                self.__shot_number += 1
                self.__sequential_number_by_shot = 0

                self.shots_summary.append({"shot_number": self.__shot_number, "timestamp": rawdata.timestamp})

            # ショット区間終了検知
            if self._detect_pulse_shot_end(rawdata.pulse):
                logger.info(
                    f"{self.__sequential_number_by_shot} samples cutted out in shot_number: {self.__shot_number}"
                )
                self.shots_summary[self.__shot_number - 1][
                    "num_of_samples_in_cut_out"
                ] = self.__sequential_number_by_shot
                self.__is_shot_section = False

            # ショット未開始ならば後続は何もしない
            if not self.__is_shot_section:
                continue

            # ここに到達するのはショット区間かつ切り出し区間
            self._add_cut_out_target(rawdata)
            self.__sequential_number += 1
            self.__sequential_number_by_shot += 1
