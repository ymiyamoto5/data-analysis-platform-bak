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
    """ データインポートクラス """

    CHUNK_SIZE: Final = 10_000_000  # csvから一度に読み出す行数
    TAIL_SIZE: Final = 1_000  # 末尾データ保持数（chunk跨ぎの際に利用）

    def __init__(self):
        self.__is_shot_section: bool = False  # ショット内か否かを判別する
        self.__is_target_of_cut_off: bool = False  # ショットの内、切り出し対象かを判別する
        self.__sequential_number: int = 0
        self.__sequential_number_by_shot: int = 0
        self.__shot_number: int = 0
        self.__shots: list = []

    # # テスト用の公開プロパティ
    # @property
    # def is_shot_section(self):
    #     return self.__is_shot_section

    # @is_shot_section.setter
    # def is_shot_section(self, is_shot_section):
    #     self.__is_shot_section = is_shot_section

    # @property
    # def is_target_of_cut_off(self):
    #     return self.__is_target_of_cut_off

    # @is_target_of_cut_off.setter
    # def is_target_of_cut_off(self, is_target_of_cut_off):
    #     self.__is_target_of_cut_off = is_target_of_cut_off

    # @property
    # def sequential_number(self):
    #     return self.__sequential_number

    # @sequential_number.setter
    # def sequential_number(self, sequential_number):
    #     self.__sequential_number = sequential_number

    # @property
    # def sequential_number_by_shot(self):
    #     return self.__sequential_number_by_shot

    # @sequential_number_by_shot.setter
    # def sequential_number_by_shot(self, sequential_number_by_shot):
    #     self.__sequential_number_by_shot = sequential_number_by_shot

    # @property
    # def shot_number(self):
    #     return self.__shot_number

    # @shot_number.setter
    # def shot_number(self, shot_number):
    #     self.__shot_number = shot_number

    @time_log
    def import_data_by_shot(
        self,
        rawdata_filename: str,
        shots_index: str,
        start_displacement: float,
        end_displacement: float,
        num_of_process: int = 8,
    ):
        """ shotデータインポート処理 """

        ElasticManager.delete_exists_index(index=shots_index)

        mapping_file = "mappings/mapping_shots.json"
        ElasticManager.create_index(index=shots_index, mapping_file=mapping_file)

        self._main_process(rawdata_filename, shots_index, start_displacement, end_displacement, num_of_process)

    @time_log
    def _main_process(
        self,
        rawdata_filename: str,
        shots_index: str,
        start_displacement: float,
        end_displacement: float,
        num_of_process: int,
    ) -> None:
        """
        csvファイルを一定行数に読み取り、ショット切り出しおよび保存を行う。

        Args:
            rawdata_filename: 生データcsvのファイル名
            shots_index: 切り出したショットの格納先となるElasticsearchのインデックス名
            start_displacement: ショット開始となる変位値
            end_displacement: ショット終了となる変位値
            num_of_process: 並列処理のプロセス数
        """

        cols = ("load01", "load02", "load03", "load04", "displacement")
        current_df_tail: DataFrame = pd.DataFrame(index=[], columns=cols)

        now = datetime.now()

        # chunksize毎に処理
        for loop_count, rawdata_df in enumerate(
            pd.read_csv(rawdata_filename, chunksize=DataImporter.CHUNK_SIZE, names=cols)
        ):
            # スループット表示
            if loop_count != 0:
                processed_count: int = loop_count * DataImporter.CHUNK_SIZE
                throughput_counter(processed_count, now)

            # chunk開始直後にショットを検知した場合、荷重開始点を含めるためにN件遡る。
            # そのためのデータをprevious_df_tail（1つ前のchunkの末尾）とcurrent_df_tail（現在のchunkの末尾）に保持しておく。
            previous_df_tail, current_df_tail = self._backup_df_tail(current_df_tail, rawdata_df)

            # chunk内のサンプルを1つずつ確認し、ショット切り出し
            shots: list = self._cut_out_shot(previous_df_tail, rawdata_df, start_displacement, end_displacement)

            # 切り出されたショットデータをElasticsearchに書き出し
            if len(shots) > 0:
                BULK_CHUNK_SIZE: Final = 5000
                ElasticManager.multi_process_bulk(shots, shots_index, num_of_process, BULK_CHUNK_SIZE)
                self.__shots = []

        logger.info("Cut_off finished.")

    def _cut_out_shot(
        self, previous_df_tail: DataFrame, rawdata_df: DataFrame, start_displacement: float, end_displacement: float
    ) -> list:
        """ ショット切り出し処理。生データの変位値を参照し、ショット対象となるデータのみをリストに含めて返す。 """

        for row_number, rawdata in enumerate(rawdata_df.itertuples()):
            # ショット開始判定
            if (not self.__is_shot_section) and (rawdata.displacement <= start_displacement):
                self.__is_shot_section = True
                self.__is_target_of_cut_off = True
                self.__shot_number += 1
                self.__sequential_number_by_shot = 0

                # 荷重立ち上がり点取りこぼし防止
                preceding_df: DataFrame = self._get_preceding_df(row_number, rawdata_df, previous_df_tail)

                for d in preceding_df.itertuples():
                    shot = {
                        "sequential_number": self.__sequential_number,
                        "sequential_number_by_shot": self.__sequential_number_by_shot,
                        "load01": d.load01,
                        "load02": d.load02,
                        "load03": d.load03,
                        "load04": d.load04,
                        "displacement": d.displacement,
                        "shot_number": self.__shot_number,
                        "tags": [],
                    }
                    self.__shots.append(shot)
                    self.__sequential_number += 1
                    self.__sequential_number_by_shot += 1

            # ショット区間の終了判定
            MARGIN: Final = 0.1  # ノイズの影響等で変位値が単調減少しなかった場合、ショット区間がすぐに終わってしまうことを防ぐためのマージン
            if self.__is_shot_section and (rawdata.displacement > start_displacement + MARGIN):
                self.__is_shot_section = False

            # ショット未開始ならば後続は何もしない
            if not self.__is_shot_section:
                continue

            # 切り出し区間の終了判定
            if rawdata.displacement <= end_displacement:
                self.__is_target_of_cut_off = False
                self.__sequential_number_by_shot = 0

            # 切り出し区間に到達していなければ後続は何もしない
            if not self.__is_target_of_cut_off:
                continue

            self.__sequential_number += 1
            self.__sequential_number_by_shot += 1

            # 切り出し対象としてリストに加える
            shot = {
                "sequential_number": self.__sequential_number,
                "sequential_number_by_shot": self.__sequential_number_by_shot,
                "load01": rawdata.load01,
                "load02": rawdata.load02,
                "load03": rawdata.load03,
                "load04": rawdata.load04,
                "displacement": rawdata.displacement,
                "shot_number": self.__shot_number,
                "tags": [],
            }
            self.__shots.append(shot)

        return self.__shots

    def _backup_df_tail(self, current_df_tail: DataFrame, df: DataFrame) -> DataFrame:
        """ 1つ前のchunkの末尾を現在のchunkの末尾に更新し、現在のchunkの末尾を保持する """

        N: Final = DataImporter.TAIL_SIZE

        previous_df_tail = current_df_tail.copy()
        current_df_tail = df[-N:].copy()

        return previous_df_tail, current_df_tail

    def _get_preceding_df(self, row_number: int, rawdata_df: DataFrame, previous_df_tail: DataFrame) -> DataFrame:
        """ ショット開始点からN件遡ったデータを取得する """

        N = DataImporter.TAIL_SIZE

        # 遡って取得するデータが現在のDataFrameに含まれる場合
        # ex) N=1000で、row_number=1500でショットを検知した場合、rawdata_df[500:1500]を取得
        if row_number >= N:
            start_index: int = row_number - N
            end_index: int = row_number
            return rawdata_df[start_index:end_index]

        # 初めのchunkでショットを検出し、遡って取得するデータが現在のDataFrameに含まれない場合
        # ex) N=1000で、初めのchunkにおいてrow_number=100でショットを検知した場合、rawdata_df[:100]を取得
        if len(previous_df_tail) == 0:
            return rawdata_df[:row_number]

        # 遡って取得するデータが現在のDataFrameに含まれない場合
        # ex) N=1000で、row_number=200でショットを検知した場合、previous_df_tail[200:] + rawdata_df[:200]を取得
        start_index: int = row_number
        end_index: int = row_number
        return pd.concat(previous_df_tail[start_index:], rawdata_df[:end_index])


def main():
    data_importer = DataImporter()
    # data_importer.import_data_by_shot("data/No13.csv", "shots-no13", 47, 34, 8)
    data_importer.import_data_by_shot("data/No13_3000.csv", "shots-no13-3000", 47, 34, 8)


if __name__ == "__main__":
    main()
