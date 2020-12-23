import os
import sys
import logging
import logging.handlers
import pandas as pd
from typing import Final
from datetime import datetime
from pandas.core.frame import DataFrame

sys.path.append(os.path.join(os.path.dirname(__file__), "../utils"))
from elastic_manager import ElasticManager
from time_logger import time_log
from throughput_counter import throughput_counter

LOG_FILE: Final = "log/cut_out_shot/cut_out_shot.log"
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


class CutOutShot:
    """ データインポートクラス """

    def __init__(self, chunk_size=10_000_000, tail_size=1_000):
        self.__chunk_size = chunk_size
        self.__tail_size = tail_size

        self.__is_shot_section: bool = False  # ショット内か否かを判別する
        self.__is_target_of_cut_out: bool = False  # ショットの内、切り出し対象かを判別する
        self.__sequential_number: int = 0
        self.__sequential_number_by_shot: int = 0
        self.__shot_number: int = 0
        # self.__shots: list = []

    # # テスト用の公開プロパティ
    # @property
    # def is_shot_section(self):
    #     return self.__is_shot_section

    # @is_shot_section.setter
    # def is_shot_section(self, is_shot_section):
    #     self.__is_shot_section = is_shot_section

    # @property
    # def is_target_of_cut_out(self):
    #     return self.__is_target_of_cut_out

    # @is_target_of_cut_out.setter
    # def is_target_of_cut_out(self, is_target_of_cut_out):
    #     self.__is_target_of_cut_out = is_target_of_cut_out

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
    def cut_out_shot(
        self,
        rawdata_filename: str,
        shots_index: str,
        start_displacement: float,
        end_displacement: float,
        back_seconds_for_tagging: int = 120,
        num_of_process: int = 8,
    ) -> None:
        """
        csvファイルをチャンクサイズ単位に読み取り、以下の処理を行う。
        * 中断区間のデータ除外
        * ショット切り出し
        * 物理変換
        * SPM計算
        * 事象記録のタグ付け
        * Elasticsearchへの保存

        Args:
            rawdata_filename: 生データcsvのファイル名
            shots_index: 切り出したショットの格納先となるElasticsearchのインデックス名
            start_displacement: ショット開始となる変位値
            end_displacement: ショット終了となる変位値
            back_seconds_for_tagging: タグ付けにおいて、何秒前まで遡るか
            num_of_process: 並列処理のプロセス数
        """

        # 同名のindexがあれば削除
        ElasticManager.delete_exists_index(index=shots_index)
        # index作成
        mapping_file = "mappings/mapping_shots.json"
        ElasticManager.create_index(index=shots_index, mapping_file=mapping_file)

        # 対応するevents_indexのデータ取得
        rawdata_suffix: str = os.path.splitext(os.path.basename(rawdata_filename))[0]
        events_index: str = "events-" + rawdata_suffix
        query = {"sort": {"event_id": {"order": "asc"}}}
        events: list = ElasticManager.get_all_doc(events_index, query)

        # events_indexから中断区間を取得
        pause_events = [x for x in events if x["event_type"] == "pause"]
        # print(pause_events)
        if len(pause_events) > 0:
            for pause_event in pause_events:
                if pause_event.get("end_time") is None:
                    logger.exception("Pause event does not finished. Please retry after finish pause.")
                    raise ValueError

        # events_indexからタグ付け区間を取得

        COLS: Final = ("timestamp", "displacement", "load01", "load02", "load03", "load04")
        previous_df_tail: DataFrame = pd.DataFrame(index=[], columns=COLS)

        procs: list = []

        NOW: Final = datetime.now()
        # chunksize毎に処理
        for loop_count, rawdata_df in enumerate(
            pd.read_csv(rawdata_filename, chunksize=self.__chunk_size, names=COLS, usecols=[1, 2, 3, 4, 5, 6])
        ):
            # スループット表示
            if loop_count != 0:
                processed_count: int = loop_count * self.__chunk_size
                throughput_counter(processed_count, NOW)

            # chunk内のサンプルを1つずつ確認し、ショット切り出し
            shots: list = self._cut_out_shot(
                previous_df_tail, rawdata_df, start_displacement, end_displacement, pause_events
            )

            # タグ付け

            # 物理変換

            # spm計算

            # 子プロセスのjoin
            if len(procs) > 0:
                for p in procs:
                    p.join()

            # 切り出されたショットデータをElasticsearchに書き出し、バッファクリア
            if len(shots) > 0:
                logger.info(f"{len(shots)} shots detected in chunk {loop_count+1}.")
                procs: list = ElasticManager.multi_process_bulk_lazy_join(
                    data=shots, index_to_import=shots_index, num_of_process=num_of_process, chunk_size=5000
                )
                shots = []

            # chunk開始直後にショットを検知した場合、荷重開始点を含めるためにN件遡る。そのためのchunk末尾バックアップ。
            previous_df_tail = self._backup_df_tail(rawdata_df)

        logger.info("Cut out finished.")

    def _is_include_in_pause_interval(self, rawdata_timestamp: datetime, pause_events: list) -> bool:
        """ 対象のサンプルが中断区間にあるか判定する """

        for pause_event in pause_events:
            start_time: datetime = datetime.fromisoformat(pause_event.get("start_time"))
            end_time: datetime = datetime.fromisoformat(pause_event.get("end_time"))

            if start_time <= rawdata_timestamp <= end_time:
                return True

        return False

    def _cut_out_shot(
        self,
        previous_df_tail: DataFrame,
        rawdata_df: DataFrame,
        start_displacement: float,
        end_displacement: float,
        pause_events: list = [],
    ) -> list:
        """ ショット切り出し処理。生データの変位値を参照し、ショット対象となるデータのみをリストに含めて返す。 """

        shots: list = []

        for row_number, rawdata in enumerate(rawdata_df.itertuples()):
            # 中断区間であれば何もしない
            if len(pause_events) > 0:
                rawdata_timestamp: datetime = datetime.fromisoformat(rawdata.timestamp)
                if self._is_include_in_pause_interval(rawdata_timestamp, pause_events):
                    continue

            # ショット開始判定
            if (not self.__is_shot_section) and (rawdata.displacement <= start_displacement):
                self.__is_shot_section = True
                self.__is_target_of_cut_out = True
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
                    shots.append(shot)
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
            if self.__is_target_of_cut_out and (rawdata.displacement <= end_displacement):
                self.__is_target_of_cut_out = False
                self.__sequential_number_by_shot = 0

            # 切り出し区間に到達していなければ後続は何もしない
            if not self.__is_target_of_cut_out:
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
            shots.append(shot)

        return shots

    def _backup_df_tail(self, df: DataFrame) -> DataFrame:
        """ 1つ前のchunkの末尾を現在のchunkの末尾に更新し、現在のchunkの末尾を保持する """

        N: Final = self.__tail_size
        return df[-N:].copy()

    def _get_preceding_df(self, row_number: int, rawdata_df: DataFrame, previous_df_tail: DataFrame) -> DataFrame:
        """ ショット開始点からN件遡ったデータを取得する """

        N: Final = self.__tail_size

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
    # cut_out_shot = CutOutShot()
    # cut_out_shot.import_data_by_shot("data/No13.csv", "shots-no13", 47, 34, 8)
    # cut_out_shot.import_data_by_shot("data/No13_3000.csv", "shots-no13-3000", 47, 34, 8)
    # cut_out_shot.cut_out_shot("data/No04.CSV", "shots-no04", 47, 34, 8)
    cut_out_shot = CutOutShot(chunk_size=1_000_000, tail_size=10)
    cut_out_shot.cut_out_shot(
        "data/pseudo_data/20201216165900/20201216165900.csv", "shots-20201216165900", 4.8, 3.4, 8
    )


if __name__ == "__main__":
    main()
