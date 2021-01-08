import multiprocessing
import os
import sys
import logging
import logging.handlers
import pandas as pd
import glob
from typing import Callable, Final, List, Tuple, Optional
from datetime import datetime, timedelta
from pandas.core.frame import DataFrame

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from elastic_manager.elastic_manager import ElasticManager

sys.path.append(os.path.join(os.path.dirname(__file__), "../utils"))
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
    def __init__(
        self,
        previous_size: int = 1_000,
        min_spm: int = 15,
        back_seconds_for_tagging: int = 120,
        num_of_process: int = 8,
        chunk_size: int = 5_000,
        margin: int = 0.1,
        displacement_func: Optional[Callable[[float], float]] = None,
        load01_func: Optional[Callable[[float], float]] = None,
        load02_func: Optional[Callable[[float], float]] = None,
        load03_func: Optional[Callable[[float], float]] = None,
        load04_func: Optional[Callable[[float], float]] = None,
    ):
        self.__previous_size: int = previous_size
        self.__min_spm: int = min_spm
        self.__back_seconds_for_tagging: int = back_seconds_for_tagging
        self.__num_of_process: int = num_of_process
        self.__chunk_size: int = chunk_size
        self.__margin: int = margin
        self.__max_samples_per_shot: int = int(60 / self.__min_spm) * common.SAMPLING_INTERVAL  # 100kサンプルにおける最大サンプル数
        self.__is_shot_section: bool = False  # ショット内か否かを判別する
        self.__is_target_of_cut_out: bool = False  # ショットの内、切り出し対象かを判別する
        self.__sequential_number: int = 0
        self.__sequential_number_by_shot: int = 0
        self.__shot_number: int = 0
        self.__previous_shot_start_time: Optional[float] = None
        self.__cut_out_targets: List[dict] = []
        self.__previous_df_tail: DataFrame = pd.DataFrame(
            index=[], columns=("timestamp", "displacement", "load01", "load02", "load03", "load04")
        )
        self.__shots_meta_df: DataFrame = pd.DataFrame(columns=("shot_number", "spm", "num_of_samples_in_cut_out"))

        if displacement_func is None:
            logger.error("displacement_func is not defined.")
            raise SystemExit
        self.__displacement_func: Optional[Callable[[float], float]] = displacement_func

        if load01_func is None:
            logger.error("load01_func is not defined.")
            raise SystemExit
        self.__load01_func: Optional[Callable[[float], float]] = load01_func

        if load02_func is None:
            logger.error("load02_func is not defined.")
            raise SystemExit
        self.__load02_func: Optional[Callable[[float], float]] = load02_func

        if load03_func is None:
            logger.error("load03_func is not defined.")
            raise SystemExit
        self.__load03_func: Optional[Callable[[float], float]] = load03_func

        if load04_func is None:
            logger.error("load04_func is not defined.")
            raise SystemExit
        self.__load04_func: Optional[Callable[[float], float]] = load04_func

    # テスト用の公開プロパティ
    @property
    def is_shot_section(self):
        return self.__is_shot_section

    @is_shot_section.setter
    def is_shot_section(self, is_shot_section: bool):
        self.__is_shot_section = is_shot_section

    @property
    def is_target_of_cut_out(self):
        return self.__is_target_of_cut_out

    @is_target_of_cut_out.setter
    def is_target_of_cut_out(self, is_target_of_cut_out: bool):
        self.__is_target_of_cut_out = is_target_of_cut_out

    @property
    def sequential_number(self):
        return self.__sequential_number

    @sequential_number.setter
    def sequential_number(self, sequential_number: int):
        self.__sequential_number = sequential_number

    @property
    def sequential_number_by_shot(self):
        return self.__sequential_number_by_shot

    @sequential_number_by_shot.setter
    def sequential_number_by_shot(self, sequential_number_by_shot: int):
        self.__sequential_number_by_shot = sequential_number_by_shot

    @property
    def shot_number(self):
        return self.__shot_number

    @shot_number.setter
    def shot_number(self, shot_number: int):
        self.__shot_number = shot_number

    @property
    def previous_shot_start_time(self):
        return self.__previous_shot_start_time

    @previous_shot_start_time.setter
    def previous_shot_start_time(self, previous_shot_start_time: Optional[float]):
        self.__previous_shot_start_time = previous_shot_start_time

    @property
    def cut_out_targets(self):
        return self.__cut_out_targets

    @cut_out_targets.setter
    def cut_out_targets(self, cut_out_targets: List[dict]):
        self.__cut_out_targets = cut_out_targets

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

    def _get_tag_events(self, events: List[dict]) -> List[dict]:
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
                tag_event["start_time"] = tag_event["end_time"] - timedelta(seconds=self.__back_seconds_for_tagging)
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

    def _get_tags(self, rawdata_timestamp: datetime, tag_events: List[dict]) -> List[str]:
        """ 対象サンプルが事象記録範囲にあるか判定し、範囲内であれば事象タグを返す """

        tags: List[str] = []
        for tag_event in tag_events:
            if tag_event["start_time"] <= rawdata_timestamp <= tag_event["end_time"]:
                tags.append(tag_event["tag"])

        return tags

    def _add_tags(self, tag_events: List[dict]) -> None:
        """ ショットデータにタグ付け """

        tags: List[str] = []

        for d in self.__cut_out_targets:
            tags: List[str] = self._get_tags(d["timestamp"], tag_events)
            if len(tags) > 0:
                d["tags"].extend(tags)

    def _detect_shot_start(self, displacement: float, start_displacement: float) -> bool:
        """ ショット開始検知。ショットが未検出かつ変位値が開始しきい値以下の場合、ショット開始とみなす。 """

        return (not self.__is_shot_section) and (displacement <= start_displacement)

    def _detect_shot_end(self, displacement: float, start_displacement: float) -> bool:
        """ ショット終了検知。ショットが検出されている状態かつ変位値が開始しきい値+マージンより大きい場合、ショット終了とみなす。

            margin: ノイズの影響等で変位値が単調減少しなかった場合、ショット区間がすぐに終わってしまうことを防ぐためのマージン
        """

        return self.__is_shot_section and (displacement > start_displacement + self.__margin)

    def _detect_cut_out_end(self, displacement: float, end_displacement: float) -> bool:
        """ 切り出し終了検知。切り出し区間として検知されており、かつ変位値が終了しきい値以下の場合、切り出し終了とみなす。"""

        return self.__is_target_of_cut_out and (displacement <= end_displacement)

    def _backup_df_tail(self, df: DataFrame) -> None:
        """ 現在のchunkの末尾を保持する """

        N: Final[int] = self.__previous_size
        self.__previous_df_tail: DataFrame = df[-N:].copy()

    def _get_preceding_df(self, row_number: int, rawdata_df: DataFrame) -> DataFrame:
        """ ショット開始点からN件遡ったデータを取得する """

        N: Final[int] = self.__previous_size

        # 遡って取得するデータが現在のDataFrameに含まれる場合
        # ex) N=1000で、row_number=1500でショットを検知した場合、rawdata_df[500:1500]を取得
        if row_number >= N:
            start_index: int = row_number - N
            end_index: int = row_number
            return rawdata_df[start_index:end_index]

        # 初めのpklでショットを検出し、遡って取得するデータが現在のDataFrameに含まれない場合
        # ex) N=1000で、初めのchunkにおいてrow_number=100でショットを検知した場合、rawdata_df[:100]を取得
        if len(self.__previous_df_tail) == 0:
            return rawdata_df[:row_number]

        # 遡って取得するデータが現在のDataFrameに含まれない場合
        # ex) N=1000で、row_number=200でショットを検知した場合、previous_df_tail[200:] + rawdata_df[:200]を取得
        start_index: int = row_number
        end_index: int = row_number
        return pd.concat([self.__previous_df_tail[start_index:], rawdata_df[:end_index]], axis=0)

    def _calculate_spm(self, timestamp: float) -> float:
        """ spm (shot per minute) 計算。ショット検出時、前ショットの開始時間との差分を計算する。 """

        spm: float = 1.0 * 60 / (timestamp - self.__previous_shot_start_time)
        logger.debug(f"shot_number: {self.__shot_number}, spm: {spm}")
        self.__previous_shot_start_time = timestamp
        return spm

    def _initialize_when_shot_detected(self) -> None:
        """ ショット検出時の初期処理 """

        self.__is_shot_section = True
        self.__is_target_of_cut_out = True  # ショット開始 = 切り出し区間開始
        self.__shot_number += 1
        self.__sequential_number_by_shot = 0

    def _include_previous_data(self, preceding_df: DataFrame) -> None:
        """ ショット検出時、previous_size分のデータを遡って切り出し対象に含める。荷重立ち上がり点取りこぼし防止のため。 """

        for d in preceding_df.itertuples():
            cut_out_target: dict = {
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
            self.__cut_out_targets.append(cut_out_target)
            self.__sequential_number += 1
            self.__sequential_number_by_shot += 1

    def _add_cut_out_target(self, rawdata: dict) -> None:
        """ 切り出し対象としてデータを追加 """

        self.__sequential_number += 1
        self.__sequential_number_by_shot += 1

        cut_out_target: dict = {
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
        self.__cut_out_targets.append(cut_out_target)

    def _set_to_none_for_low_spm(self) -> None:
        """ 切り出したショットの内、最低spmを下回るショットのspmはNoneに設定する """

        self.__shots_meta_df["spm"] = self.__shots_meta_df["spm"].where(
            self.__shots_meta_df["spm"] >= self.__min_spm, None
        )

    def _exclude_over_sample(self, df: DataFrame) -> DataFrame:
        """ 切り出したショットの内、最大サンプル数を上回るショットを除外したDataFrameを返す """

        over_sample_df: DataFrame = self.__shots_meta_df[
            self.__shots_meta_df["num_of_samples_in_cut_out"] > self.__max_samples_per_shot
        ]

        if len(over_sample_df) == 0:
            return df

        over_sample_shot_numbers: List[float] = list(over_sample_df.shot_number)

        return df.query("shot_number not in @over_sample_shot_numbers")

    def _apply_expr_displacement(self, df: DataFrame) -> DataFrame:
        """ 変位値に対して変換式を適用 """

        if self.__displacement_func is not None:
            df["displacement"] = df["displacement"].apply(self.__displacement_func)

        return df

    def _apply_expr_load(self, df: DataFrame) -> DataFrame:
        """ 荷重値に対して変換式を適用 """

        df["load01"] = df["load01"].apply(self.__load01_func)
        df["load02"] = df["load02"].apply(self.__load02_func)
        df["load03"] = df["load03"].apply(self.__load03_func)
        df["load04"] = df["load04"].apply(self.__load04_func)

        return df

    def _export_shots_meta_to_es(self, shots_meta_index: str):
        """ ショットメタデータをshots_metaインデックスに出力 """

        self.__shots_meta_df["shot_number"] = self.__shots_meta_df["shot_number"].astype(int)

        shots_meta_data: List[dict] = self.__shots_meta_df.to_dict(orient="records")

        procs = ElasticManager.multi_process_bulk_lazy_join(
            data=shots_meta_data, index_to_import=shots_meta_index, num_of_process=self.__num_of_process
        )
        procs = self.__join_process(procs)

    def __join_process(self, procs: List[multiprocessing.context.Process]) -> List:
        """ マルチプロセスの処理待ち """

        if len(procs) > 0:
            for p in procs:
                p.join()

        return []

    @time_log
    def cut_out_shot(self, rawdata_dir_name: str, start_displacement: float, end_displacement: float,) -> None:
        """
        csvファイルをチャンクサイズ単位に読み取り、以下の処理を行う。
        * 中断区間のデータ除外
        * ショット切り出し
        * 物理変換
        * SPM計算
        * SPMしきい値以下のデータ除外
        * 事象記録のタグ付け
        * Elasticsearchへの保存

        Args:
            rawdata_filename: 生データcsvのファイル名
            start_displacement: ショット開始となる変位値
            end_displacement: ショット終了となる変位値
            back_seconds_for_tagging: タグ付けにおいて、遡る秒数
        """

        shots_index: str = "shots-" + rawdata_dir_name
        ElasticManager.delete_exists_index(index=shots_index)
        ElasticManager.create_index(index=shots_index, mapping_file="mappings/mapping_shots.json")

        shots_meta_index: str = "shots-meta-" + rawdata_dir_name
        ElasticManager.delete_exists_index(index=shots_meta_index)
        ElasticManager.create_index(index=shots_meta_index, mapping_file="mappings/mapping_shots_meta.json")

        # event_indexから各種イベント情報を取得する
        events: List[dict] = self._get_events(suffix=rawdata_dir_name)
        collect_start_time: float = self._get_collect_start_time(events)
        pause_events: List[dict] = self._get_pause_events(events)
        tag_events: List[dict] = self._get_tag_events(events)

        procs: List[multiprocessing.context.Process] = []
        processed_count: int = 0

        NOW: Final[datetime] = datetime.now()

        # 取り込むpickleファイルのリストを取得
        data_dir: str = common.get_config_value("app_config.json", "data_dir")
        rawdata_dir_path: str = os.path.join(data_dir, rawdata_dir_name)
        pickle_files: List[str] = self._get_pickle_list(rawdata_dir_path)

        # main loop
        for loop_count, pickle_file in enumerate(pickle_files):
            rawdata_df: DataFrame = pd.read_pickle(pickle_file)

            # 段取区間の除外
            rawdata_df = self._exclude_setup_interval(rawdata_df, collect_start_time)

            # 中断区間の除外
            if len(pause_events) > 0:
                rawdata_df = self._exclude_pause_interval(rawdata_df, pause_events)

            # TODO: 変位値を物理変換

            # 変位値に変換式適用
            rawdata_df = self._apply_expr_displacement(rawdata_df)

            # ショット切り出し
            self._cut_out_shot(rawdata_df, start_displacement, end_displacement)

            # 現在のファイルに含まれる末尾データをバックアップ。ファイル開始直後にショットを検知した場合、このバックアップからデータを得る。
            self._backup_df_tail(rawdata_df)

            # スループット表示
            if loop_count != 0:
                processed_count += len(rawdata_df)
                throughput_counter(processed_count, NOW)

            # ショットがなければ以降の処理はスキップ
            if len(self.__cut_out_targets) == 0:
                logger.info(f"Shot is not detected in {pickle_file}")
                continue

            # NOTE: 以下処理のため一時的にDataFrameに変換している。
            cut_out_df: DataFrame = pd.DataFrame(self.__cut_out_targets)

            # 最大サンプル数を超えたショットの削除
            cut_out_df: DataFrame = self._exclude_over_sample(cut_out_df)

            if len(cut_out_df) == 0:
                logger.info(f"Shot is not detected in {pickle_file} by over_sample_filter.")
                continue

            # 荷重値に変換式を適用
            cut_out_df: DataFrame = self._apply_expr_load(cut_out_df)

            # Elasticsearchに格納するため、dictに戻す
            self.__cut_out_targets: List[dict] = cut_out_df.to_dict(orient="records")

            # タグ付け
            if len(tag_events) > 0:
                self._add_tags(tag_events)

            logger.info(f"{len(self.__cut_out_targets)} shots detected in {pickle_file}.")

            # 子プロセスのjoin
            procs = self.__join_process(procs)

            # Elasticsearchに出力
            procs = ElasticManager.multi_process_bulk_lazy_join(
                data=self.__cut_out_targets,
                index_to_import=shots_index,
                num_of_process=self.__num_of_process,
                chunk_size=self.__chunk_size,
            )

            self.__cut_out_targets = []

        # 全ファイル走査後、子プロセスが残っていればjoin
        procs = self.__join_process(procs)

        # spmがしきい値以下の場合、Noneとする。
        self._set_to_none_for_low_spm()

        # ショットメタデータをElasticsearchに出力
        self._export_shots_meta_to_es(shots_meta_index)

    def _cut_out_shot(self, rawdata_df: DataFrame, start_displacement: float, end_displacement: float):
        """ ショット切り出し処理。生データの変位値を参照し、ショット対象となるデータのみをリストに含めて返す。 """

        for row_number, rawdata in enumerate(rawdata_df.itertuples()):
            if self._detect_shot_start(rawdata.displacement, start_displacement):
                # 最初のショット検知時はspm計算できない。
                if self.__shot_number == 0:
                    self.__previous_shot_start_time: float = rawdata.timestamp
                # 2つめ以降のショット検知時は、1つ前のショットのspmを計算して記録する
                else:
                    spm: float = self._calculate_spm(rawdata.timestamp)
                    self.__shots_meta_df = self.__shots_meta_df.append(
                        {
                            "shot_number": self.__shot_number,
                            "spm": spm,
                            "num_of_samples_in_cut_out": self.__sequential_number_by_shot,
                        },
                        ignore_index=True,
                    )

                self._initialize_when_shot_detected()

                # 荷重開始点取りこぼし防止
                preceding_df: DataFrame = self._get_preceding_df(row_number, rawdata_df)
                self._include_previous_data(preceding_df)

            if self._detect_shot_end(rawdata.displacement, start_displacement):
                self.__is_shot_section = False

            # ショット未開始ならば後続は何もしない
            if not self.__is_shot_section:
                continue

            if self._detect_cut_out_end(rawdata.displacement, end_displacement):
                self.__is_target_of_cut_out = False

            # 切り出し区間でなければ後続は何もしない
            if not self.__is_target_of_cut_out:
                continue

            # ここに到達するのはショット区間かつ切り出し区間
            self._add_cut_out_target(rawdata)


def main():
    # No13 3000shot拡張。切り出し後のデータ数：9,287,421
    displacement_func = lambda x: x * 1.0
    load01_func = lambda x: x * 1.0
    load02_func = lambda x: x * 2.0
    load03_func = lambda x: x * 3.0
    load04_func = lambda x: x * 4.0

    cut_out_shot = CutOutShot(
        min_spm=15,
        back_seconds_for_tagging=120,
        previous_size=1_000,
        num_of_process=12,
        chunk_size=5_000,
        margin=0.1,
        displacement_func=displacement_func,
        load01_func=load01_func,
        load02_func=load02_func,
        load03_func=load03_func,
        load04_func=load04_func,
    )
    cut_out_shot.cut_out_shot(rawdata_dir_name="20201201010000", start_displacement=47, end_displacement=34)

    # 任意波形生成
    # cut_out_shot = CutOutShot(previous_size=10)
    # cut_out_shot.cut_out_shot("20201216165900", 4.8, 3.4, 20, 12)


if __name__ == "__main__":
    main()
