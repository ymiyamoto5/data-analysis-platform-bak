from typing import List

from backend.app.models.data_collect_history_detail import DataCollectHistorySensor
from backend.common.common_logger import logger
from pandas.core.frame import DataFrame


class StrokeDisplacementCutter:
    def __init__(
        self,
        start_stroke_displacement: float,
        end_stroke_displacement: float,
        margin: float,
        sensors: List[DataCollectHistorySensor],
    ):
        self.__start_stroke_displacement: float = start_stroke_displacement
        self.__end_stroke_displacement: float = end_stroke_displacement
        self.__margin: float = margin
        self.__shot_number: int = 0
        self.__sequential_number: int = 0
        self.__sequential_number_by_shot: int = 0
        self.__is_shot_section: bool = False  # ショット内か否かを判別する
        self.__is_target_of_cut_out: bool = False  # ショットの内、切り出し対象かを判別する
        self.__sensors: List[DataCollectHistorySensor] = sensors
        self.cut_out_targets: List[dict] = []
        self.shots_summary: List[dict] = []

    def _detect_shot_start(self, stroke_displacement: float) -> bool:
        """ショット開始検知。ショットが未検出かつストローク変位値が終了しきい値以上開始しきい値以下の場合、ショット開始とみなす。"""

        return (not self.__is_shot_section) and (self.__end_stroke_displacement <= stroke_displacement <= self.__start_stroke_displacement)

    def _detect_shot_end(self, stroke_displacement: float) -> bool:
        """ショット終了検知。ショットが検出されている状態かつストローク変位値が開始しきい値+マージンより大きい場合、ショット終了とみなす。

        margin: ノイズの影響等でストローク変位値が単調減少しなかった場合、ショット区間がすぐに終わってしまうことを防ぐためのマージン
        """

        return self.__is_shot_section and (stroke_displacement > self.__start_stroke_displacement + self.__margin)

    def _detect_cut_out_end(self, stroke_displacement: float) -> bool:
        """切り出し終了検知。切り出し区間として検知されており、かつストローク変位値が終了しきい値以下の場合、切り出し終了とみなす。"""

        return self.__is_target_of_cut_out and (stroke_displacement <= self.__end_stroke_displacement)

    def _add_cut_out_target(self, rawdata) -> None:
        """切り出し対象としてデータを追加
        TODO: 共通化
        """

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
        """ショット切り出し処理。生データのストローク変位値を参照し、ショット対象となるデータのみをリストに含めて返す。"""

        for rawdata in rawdata_df.itertuples():
            if self._detect_shot_start(rawdata.stroke_displacement):
                self.__is_shot_section = True  # ショット開始
                self.__is_target_of_cut_out = True  # ショット開始 = 切り出し区間開始
                self.__shot_number += 1
                self.__sequential_number_by_shot = 0

                self.shots_summary.append({"shot_number": self.__shot_number, "timestamp": rawdata.timestamp})

            # ショット区間終了判定
            if self._detect_shot_end(rawdata.stroke_displacement):
                self.__is_shot_section = False

            # ショット未開始ならば後続は何もしない
            if not self.__is_shot_section:
                continue

            # 切り出し区間終了判定
            if self._detect_cut_out_end(rawdata.stroke_displacement):
                logger.info(f"{self.__sequential_number_by_shot} samples cutted out in shot_number: {self.__shot_number}")
                self.shots_summary[self.__shot_number - 1]["num_of_samples_in_cut_out"] = self.__sequential_number_by_shot
                self.__is_target_of_cut_out = False

            # 切り出し区間でなければ後続は何もしない
            if not self.__is_target_of_cut_out:
                continue

            # ここに到達するのはショット区間かつ切り出し区間
            self._add_cut_out_target(rawdata)
            self.__sequential_number += 1
            self.__sequential_number_by_shot += 1
