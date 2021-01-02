import multiprocessing
import os
import sys
import logging
import logging.handlers
import pandas as pd
import glob
from typing import Final, List, Tuple, Optional
from datetime import datetime, timedelta
from pandas.core.frame import DataFrame

sys.path.append(os.path.join(os.path.dirname(__file__), "../utils"))
from elastic_manager import ElasticManager
from time_logger import time_log
from throughput_counter import throughput_counter
import common

LOG_FILE: Final[str] = "log/cut_out_shot/cut_out_shot.log"
MAX_LOG_SIZE: Final[int] = 1024 * 1024  # 1MB

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

    def __init__(self, tail_size=1_000):
        self.__tail_size = tail_size
        self.__is_shot_section: bool = False  # ショット内か否かを判別する
        self.__is_target_of_cut_out: bool = False  # ショットの内、切り出し対象かを判別する
        self.__sequential_number: int = 0
        self.__sequential_number_by_shot: int = 0
        self.__shot_number: int = 0
        self.__previous_shot_start_time: float = None
        self.__shots: List[dict] = []

    # テスト用の公開プロパティ
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

    def _create_shots_index(self, shots_index: str) -> None:
        """ shots_indexの作成。既存のインデックスは削除。 """

        ElasticManager.delete_exists_index(index=shots_index)

        mapping_file: str = "mappings/mapping_shots.json"
        ElasticManager.create_index(index=shots_index, mapping_file=mapping_file)

    def _get_events(self, suffix: str) -> List[dict]:
        """ 対応するevents_indexのデータ取得 """

        events_index: str = "events-" + suffix
        query: dict = {"sort": {"event_id": {"order": "asc"}}}
        events: List[dict] = ElasticManager.get_all_doc(events_index, query)

        return events

    def _get_collect_start_time(self, events: List[dict]) -> float:
        """ events_indexから収集開始時間を取得 """

        start_events: List[dict] = [x for x in events if x["event_type"] == "start"]
        if len(start_events) == 0:
            logger.exception("Data collection has not started yet.")
            raise ValueError
        start_event: dict = start_events[0]
        collect_start_time: float = datetime.fromisoformat(start_event["occurred_time"]).timestamp()

        return collect_start_time

    def _get_pause_events(self, events: List[dict]) -> List[dict]:
        """ events_indexから中断イベントを取得。時刻はunixtimeに変換する。 """

        pause_events: List[dict] = [x for x in events if x["event_type"] == "pause"]
        logger.debug(pause_events)

        if len(pause_events) > 0:
            for pause_event in pause_events:
                if pause_event.get("start_time") is None:
                    logger.exception("Invalid status in pause event. Not found [start_time] key.")
                    raise KeyError

                if pause_event.get("end_time") is None:
                    logger.exception("Pause event does not finished. Please retry after finish pause.")
                    raise KeyError
                # str to datetime
                pause_event["start_time"] = datetime.fromisoformat(pause_event["start_time"])
                pause_event["end_time"] = datetime.fromisoformat(pause_event["end_time"])

                # datetime to unixtime
                pause_event["start_time"] = pause_event["start_time"].timestamp()
                pause_event["end_time"] = pause_event["end_time"].timestamp()

        return pause_events

    def _get_tag_events(self, events: List[dict], back_seconds_for_tagging) -> List[dict]:
        """ events_indexからタグ付け区間を取得。
            記録された時刻（end_time）からN秒前(back_seconds_for_tagging)に遡り、start_timeとする。
        """

        tag_events: List[dict] = [x for x in events if x["event_type"] == "tag"]
        logger.debug(tag_events)

        if len(tag_events) > 0:
            for tag_event in tag_events:
                if tag_event.get("end_time") is None:
                    logger.exception("Invalid status in tag event. Not found [end_time] key.")
                    raise KeyError

                tag_event["end_time"] = datetime.fromisoformat(tag_event["end_time"])
                tag_event["start_time"] = tag_event["end_time"] - timedelta(seconds=back_seconds_for_tagging)
                # datetime to unixtime
                tag_event["start_time"] = tag_event["start_time"].timestamp()
                tag_event["end_time"] = tag_event["end_time"].timestamp()

        return tag_events

    def _get_pickle_list(self, rawdata_dir_path: str) -> List[str]:
        """ 取り込むファイルのリストを取得する """

        pickle_file_list: List[str] = glob.glob(os.path.join(rawdata_dir_path, "*.pkl"))
        pickle_file_list.sort()

        return pickle_file_list

    def _exclude_setup_interval(self, df: DataFrame, collect_start_time: float) -> DataFrame:
        """ 収集開始前(段取中)のデータを除外 """

        return df[df["timestamp"] >= collect_start_time]

    def _exclude_pause_interval(self, df: DataFrame, pause_events: List[dict]) -> DataFrame:
        """ 中断区間のデータを除外 """

        for pause_event in pause_events:
            df = df[(df["timestamp"] < pause_event["start_time"]) | (pause_event["end_time"] < df["timestamp"])]

        return df

    def _add_tags(self, tag_events: List[dict]) -> None:
        """ ショットデータにタグ付け """

        tags: List[str] = []

        for d in self.__shots:
            tags: List[str] = self._get_tags(d["timestamp"], tag_events)
            if len(tags) > 0:
                d["tags"].extend(tags)

    def _get_tags(self, rawdata_timestamp: datetime, tag_events: List[dict]) -> List[str]:
        """ 対象サンプルが事象記録範囲にあるか判定し、範囲内であれば事象タグを返す """

        tags: List[str] = []
        for tag_event in tag_events:
            if tag_event["start_time"] <= rawdata_timestamp <= tag_event["end_time"]:
                tags.append(tag_event["tag"])

        return tags

    def _detect_shot(self, displacement: float, start_displacement: float):
        """ ショット検知。ショットが未検出かつ変位値が開始しきい値以下の場合、ショット開始とみなす。 """

        return (not self.__is_shot_section) and (displacement <= start_displacement)

    def _backup_df_tail(self, df: DataFrame) -> DataFrame:
        """ 1つ前のchunkの末尾を現在のchunkの末尾に更新し、現在のchunkの末尾を保持する """

        N: Final[int] = self.__tail_size
        return df[-N:].copy()

    def _get_preceding_df(self, row_number: int, rawdata_df: DataFrame, previous_df_tail: DataFrame) -> DataFrame:
        """ ショット開始点からN件遡ったデータを取得する """

        N: Final[int] = self.__tail_size

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
        return pd.concat([previous_df_tail[start_index:], rawdata_df[:end_index]], axis=0)

    def _calculate_spm(self, timestamp: float) -> Optional[float]:
        """ spm (shot per minute) 計算。ショット検出時、前ショットの開始時間との差分を計算する。 """

        # 最初のショット検知時はspm計算できないため、timestampだけ保持しておく
        if self.__shot_number == 0:
            self.__previous_shot_start_time: float = timestamp
            return None
        else:
            spm: float = 1.0 * 60 / (timestamp - self.__previous_shot_start_time)
            logger.debug(f"shot_number: {self.__shot_number}, spm: {spm}")
            self.__previous_shot_start_time = timestamp
            return spm

    def _initialize_when_shot_detected(self, row_number: int, rawdata_df: DataFrame, previous_df_tail: DataFrame):
        """ ショット検出時の初期処理 """

        self.__is_shot_section = True
        self.__is_target_of_cut_out = True
        self.__shot_number += 1
        self.__sequential_number_by_shot = 0

        preceding_df: DataFrame = self._get_preceding_df(row_number, rawdata_df, previous_df_tail)

        self._include_previous_data_in_shot(preceding_df)

    def _include_previous_data_in_shot(self, preceding_df: DataFrame):
        """ ショット検出時、tail_size分のデータを遡ってショットに含める。荷重立ち上がり点取りこぼし防止のため。 """

        for d in preceding_df.itertuples():
            shot: dict = {
                "timestamp": d.timestamp,
                "sequential_number": self.__sequential_number,
                "sequential_number_by_shot": self.__sequential_number_by_shot,
                "displacement": d.displacement,
                "load01": d.load01,
                "load02": d.load02,
                "load03": d.load03,
                "load04": d.load04,
                "shot_number": self.__shot_number,
                "tags": [],
            }
            self.__shots.append(shot)
            self.__sequential_number += 1
            self.__sequential_number_by_shot += 1

    @time_log
    def cut_out_shot(
        self,
        rawdata_dir_name: str,
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
            start_displacement: ショット開始となる変位値
            end_displacement: ショット終了となる変位値
            back_seconds_for_tagging: タグ付けにおいて、何秒前まで遡るか
            num_of_process: 並列処理のプロセス数
        """

        shots_index: str = "shots-" + rawdata_dir_name
        self._create_shots_index(shots_index)

        events: List[dict] = self._get_events(suffix=rawdata_dir_name)

        collect_start_time: float = self._get_collect_start_time(events)
        pause_events: List[dict] = self._get_pause_events(events)
        tag_events: List[dict] = self._get_tag_events(events, back_seconds_for_tagging)

        COLS: Final[Tuple[str]] = ("timestamp", "displacement", "load01", "load02", "load03", "load04")
        previous_df_tail: DataFrame = pd.DataFrame(index=[], columns=COLS)
        procs: List[multiprocessing.context.Process] = []
        processed_count: int = 0

        NOW: Final[datetime] = datetime.now()

        settings_file_path: str = os.path.dirname(__file__) + "/../common/app_config.json"
        data_dir = common.get_settings_value(settings_file_path, "data_dir")
        rawdata_dir_path: str = os.path.join(data_dir, rawdata_dir_name)
        pickle_files: List[str] = self._get_pickle_list(rawdata_dir_path)

        for loop_count, pickle_file in enumerate(pickle_files):
            rawdata_df: DataFrame = pd.read_pickle(pickle_file)

            rawdata_df = self._exclude_setup_interval(rawdata_df, collect_start_time)

            if len(pause_events) > 0:
                rawdata_df = self._exclude_pause_interval(rawdata_df, pause_events)

            # TODO: 物理変換

            self._cut_out_shot(previous_df_tail, rawdata_df, start_displacement, end_displacement)

            # 子プロセスのjoin
            if len(procs) > 0:
                for p in procs:
                    p.join()

            # スループット表示
            if loop_count != 0:
                processed_count += len(rawdata_df)
                throughput_counter(processed_count, NOW)

            # ショットがなければ以降の処理はスキップ
            if len(self.__shots) == 0:
                logger.info(f"Shot is not detected in {pickle_file}")
                continue

            if len(tag_events) > 0:
                self._add_tags(tag_events)

            # ショットデータをElasticsearchに書き出し
            logger.info(f"{len(self.__shots)} shots detected in {pickle_file}.")
            procs = ElasticManager.multi_process_bulk_lazy_join(
                data=self.__shots, index_to_import=shots_index, num_of_process=num_of_process, chunk_size=5000
            )
            self.__shots = []

            # chunk開始直後にショットを検知した場合、荷重開始点を含めるためにN件遡る。そのためのchunk末尾バックアップ。
            previous_df_tail: DataFrame = self._backup_df_tail(rawdata_df)

        # TODO: 低spmのshot削除

    def _cut_out_shot(
        self, previous_df_tail: DataFrame, rawdata_df: DataFrame, start_displacement: float, end_displacement: float
    ):
        """ ショット切り出し処理。生データの変位値を参照し、ショット対象となるデータのみをリストに含めて返す。 """

        for row_number, rawdata in enumerate(rawdata_df.itertuples()):
            if self._detect_shot(rawdata.displacement, start_displacement):
                spm: Optional[float] = self._calculate_spm(rawdata.timestamp)
                self._initialize_when_shot_detected(row_number, rawdata_df, previous_df_tail)

            # ショット区間の終了判定
            MARGIN: Final[float] = 0.1  # ノイズの影響等で変位値が単調減少しなかった場合、ショット区間がすぐに終わってしまうことを防ぐためのマージン
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

            # ここに到達するのはショット区間かつ切り出し区間
            self.__sequential_number += 1
            self.__sequential_number_by_shot += 1

            # 切り出し対象としてリストに加える
            shot: dict = {
                "timestamp": rawdata.timestamp,
                "sequential_number": self.__sequential_number,
                "sequential_number_by_shot": self.__sequential_number_by_shot,
                "displacement": rawdata.displacement,
                "load01": rawdata.load01,
                "load02": rawdata.load02,
                "load03": rawdata.load03,
                "load04": rawdata.load04,
                "shot_number": self.__shot_number,
                "tags": [],
            }
            self.__shots.append(shot)


def main():
    # No13 3000shot拡張。切り出し後のデータ数：9,287,537
    cut_out_shot = CutOutShot()
    cut_out_shot.cut_out_shot("20201201010000", 47, 34, 20, 8)

    # 任意波形生成
    # cut_out_shot = CutOutShot(tail_size=10)
    # cut_out_shot.cut_out_shot("20201216165900", 4.8, 3.4, 20, 8)


if __name__ == "__main__":
    main()
