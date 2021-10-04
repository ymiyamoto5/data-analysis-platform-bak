from typing import List

from backend.app.models.sensor import Sensor
from pandas.core.frame import DataFrame


class PulseCutter:
    def __init__(self, threshold: float, margin: float):
        self.__threshold = threshold
        self.__margin = margin
        self.__shot_number: int = 0
        self.__sequential_number: int = 0
        self.__sequential_number_by_shot: int = 0
        self.__is_shot_section: bool = False  # ショット内か否かを判別する
        self.__is_target_of_cut_out: bool = False  # ショットの内、切り出し対象かを判別する
        self.cut_out_targets: List[dict] = []
        self.shots_summary: List[dict] = []


#     def _detect_pulse_shot_start(self, pulse: float, threshold: float) -> bool:
#         """ショット開始検知。ショットが未検出かつパルスがしきい値以上の場合、ショット開始とみなす。"""

#         return (not self.__is_shot_section) and (pulse >= self.__threshold)

#     def _detect_pulse_shot_end(self, pulse: float) -> bool:
#         """ショット終了検知。ショットが検出されている状態かつパルスがしきい値を下回ったとき、ショット終了とみなす。"""

#         return self.__is_shot_section and (pulse < self.__threshold)

#     def cut_out_shot(self, rawdata_df: DataFrame) -> None:
#         """パルス信号によるショット切り出し
#         パルス値がしきい値を超えたタイミングでショット区間開始
#         メタ情報を記録
#         以降、ループごとにパルス値を確認し、しきい値を下回っていたらショット区間終了
#         """

#         for row_number, rawdata in enumerate(rawdata_df.itertuples()):
#             # pulseがしきい値以上のとき、ショットとして記録開始
#             if self._detect_pulse_shot_start(rawdata.pulse, threshold):
#                 if self.__shot_number == 0:
#                     self.__previous_shot_start_time = rawdata.timestamp
#                 # 2つめ以降のショット検知時は、1つ前のショットのspmを計算して記録する
#                 else:
#                     spm: Optional[float] = self._calculate_spm(rawdata.timestamp)

#                     if self.__previous_shot_start_time is None:
#                         logger.error("self.__previous_shot_start_time should not be None.")
#                         sys.exit(1)

#                     self.__shots_meta_df = self.__shots_meta_df.append(
#                         {
#                             "timestamp": datetime.fromtimestamp(self.__previous_shot_start_time),
#                             "shot_number": self.__shot_number,
#                             "spm": spm,
#                             "num_of_samples_in_cut_out": self.__sequential_number_by_shot,
#                         },
#                         ignore_index=True,
#                     )
#                     self.__previous_shot_start_time = rawdata.timestamp

#                 self._initialize_when_shot_detected()

#             if self._detect_pulse_shot_end(rawdata.pulse, threshold):
#                 self.__is_shot_section = False

#             # ショット未開始ならば後続は何もしない
#             if not self.__is_shot_section:
#                 continue

#             # ここに到達するのはショット区間かつ切り出し区間
#             self._add_cut_out_target(rawdata)
