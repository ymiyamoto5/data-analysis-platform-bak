from typing import Final
from datetime import datetime
from pandas.core.frame import DataFrame

import logging
import logging.handlers
import pandas as pd

from elastic_manager import ElasticManager
from time_logger import time_log
from throughput_counter import throughput_counter

LOG_FILE: Final = "log/data_importer/data_importer.log"
MAX_LOG_SIZE: Final = 1024 * 1024  # 1MB

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=MAX_LOG_SIZE, backupCount=5),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class DataImporter:
    """
     データインポートクラス

     TODO:
           from elasticsearch(生データ) to elasticsearch処理追加
           meta_index作成
    """

    @time_log
    def import_data_by_shot(
        self,
        rawdata_filename: str,
        shots_index: str,
        start_displacement: float,
        end_displacement: float,
        num_of_process: int = 4,
    ):
        """ shotデータインポート処理 """

        mapping_file = "mappings/mapping_shots.json"

        ElasticManager.delete_exists_index(index=shots_index)
        ElasticManager.create_index(index=shots_index, mapping_file=mapping_file)

        self._cut_out_shot_from_csv(
            rawdata_filename, shots_index, start_displacement, end_displacement, num_of_process
        )

    @time_log
    def _cut_out_shot_from_csv(
        self,
        rawdata_filename: str,
        shots_index: str,
        start_displacement: float,
        end_displacement: float,
        num_of_process: int,
    ) -> None:
        """
        ショット切り出し処理。生データの変位値を参照し、ショット対象となるデータのみをリストに含めて返す。

        Args:
            rawdata_filename: 生データcsvのファイル名
            start_displacement: ショット開始となる変位値
            end_displacement: ショット終了となる変位値

        """

        is_shot_section: bool = False  # ショット内か否かを判別する
        is_target_of_cut_off: bool = False  # ショットの内、切り出し対象かを判別する
        sequential_number: int = 0
        sequential_number_by_shot: int = 0
        shot_number: int = 0
        shots: list = []

        CHUNKSIZE: Final = 10_000_000
        TAIL_SIZE: Final = 1_000

        cols = ("load01", "load02", "load03", "load04", "displacement")
        current_df_tail: DataFrame = pd.DataFrame(index=[], columns=cols)
        previous_df_tail: DataFrame = pd.DataFrame(index=[], columns=cols)

        dt_now = datetime.now()

        for loop_count, rawdata_df in enumerate(pd.read_csv(rawdata_filename, chunksize=CHUNKSIZE, names=cols)):
            processed_count: int = loop_count * CHUNKSIZE
            throughput_counter(processed_count, dt_now)

            # chunk開始直後にショットを検知した場合、N件遡るためのデータを保持しておく必要がある。
            if loop_count == 0:
                current_df_tail = rawdata_df[-TAIL_SIZE:]
            else:
                previous_df_tail = current_df_tail
                current_df_tail = rawdata_df[-TAIL_SIZE:]

            for row_number, rawdata in enumerate(rawdata_df.itertuples()):
                # ショット開始判定
                if (not is_shot_section) and (rawdata.displacement <= start_displacement):
                    is_shot_section = True
                    is_target_of_cut_off = True
                    shot_number += 1
                    sequential_number_by_shot = 0

                    # N件遡ってshotsに加える。
                    # 遡って取得するデータが現在のDataFrameに含まれる場合
                    if row_number >= TAIL_SIZE:
                        # ショットを検知したところから1,000件遡ってデータを取得
                        start_index: int = row_number - TAIL_SIZE
                        end_index: int = row_number
                        preceding_df = rawdata_df[start_index:end_index]

                    # 遡って取得するデータが現在のDataFrameに含まれない場合
                    else:
                        # 含まれない範囲のデータを過去のDataFrameから取得
                        start_index: int = row_number
                        end_index: int = TAIL_SIZE - row_number
                        preceding_df = pd.concat(previous_df_tail[start_index:], rawdata_df[:end_index])

                    for d in preceding_df.itertuples():
                        shot = {
                            "sequential_number": sequential_number,
                            "sequential_number_by_shot": sequential_number_by_shot,
                            "load01": d.load01,
                            "load02": d.load02,
                            "load03": d.load03,
                            "load04": d.load04,
                            "displacement": d.displacement,
                            "shot_number": shot_number,
                            "tags": [],
                        }
                        shots.append(shot)
                        sequential_number += 1
                        sequential_number_by_shot += 1

                # ショット区間の終了判定

                MARGIN: Final = 0.1  # ノイズの影響等で変位値が単調減少しなかった場合、ショット区間がすぐに終わってしまうことを防ぐためのバッファ
                if is_shot_section and (rawdata.displacement > start_displacement + MARGIN):
                    is_shot_section = False

                # ショット未開始ならば後続は何もしない
                if not is_shot_section:
                    continue

                # 切り出し区間の終了判定
                if rawdata.displacement <= end_displacement:
                    is_target_of_cut_off = False
                    sequential_number_by_shot = 0

                # 切り出し区間に到達していなければ後続は何もしない
                if not is_target_of_cut_off:
                    continue

                sequential_number += 1
                sequential_number_by_shot += 1

                # 切り出し対象としてリストに加える
                shot = {
                    "sequential_number": sequential_number,
                    "sequential_number_by_shot": sequential_number_by_shot,
                    "load01": rawdata.load01,
                    "load02": rawdata.load02,
                    "load03": rawdata.load03,
                    "load04": rawdata.load04,
                    "displacement": rawdata.displacement,
                    "shot_number": shot_number,
                    "tags": [],
                }
                shots.append(shot)

            # Elasticsearchに書き出し
            if len(shots) > 0:
                ElasticManager.multi_process_bulk(shots, shots_index, num_of_process, 5000)
                shots = []
        # end of all rawdata loop

        dt_now = datetime.now()
        logger.info("Cut_off finished.")


def main():
    data_importer = DataImporter()
    data_importer.import_data_by_shot("data/No13_3000.csv", "shots-no13-3000", 47, 34, 8)


if __name__ == "__main__":
    main()
