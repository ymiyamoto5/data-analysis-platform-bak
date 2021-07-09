"""
 ==================================
  cut_out_shot.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import multiprocessing
import os
import sys
import logging
import logging.handlers
import pandas as pd
import glob
from typing import Callable, Final, List, Optional
from datetime import datetime, timedelta
from pandas.core.frame import DataFrame

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from elastic_manager.elastic_manager import ElasticManager
from tag_manager.tag_manager import TagManager

sys.path.append(os.path.join(os.path.dirname(__file__), "../utils"))
from throughput_counter import throughput_counter  # type: ignore
import common

logger = logging.getLogger(__name__)


class CutOutShot:
    def __init__(
        self,
        previous_size: int = 1000,
        min_spm: int = 15,
        back_seconds_for_tagging: int = 120,
        num_of_process: int = common.NUM_OF_PROCESS,
        chunk_size: int = 5_000,
        margin: float = 0.3,
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
        self.__margin: float = margin
        self.__max_samples_per_shot: int = int(60 / self.__min_spm) * common.SAMPLING_RATE  # 100kサンプルにおける最大サンプル数
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
        self.__shots_meta_df: DataFrame = pd.DataFrame(
            columns=("timestamp", "shot_number", "spm", "num_of_samples_in_cut_out")
        )

        if displacement_func is None:
            logger.error("displacement_func is not defined.")
            sys.exit(1)
        self.__displacement_func: Optional[Callable[[float], float]] = displacement_func

        if load01_func is None:
            logger.error("load01_func is not defined.")
            sys.exit(1)
        self.__load01_func: Optional[Callable[[float], float]] = load01_func

        if load02_func is None:
            logger.error("load02_func is not defined.")
            sys.exit(1)
        self.__load02_func: Optional[Callable[[float], float]] = load02_func

        if load03_func is None:
            logger.error("load03_func is not defined.")
            sys.exit(1)
        self.__load03_func: Optional[Callable[[float], float]] = load03_func

        if load04_func is None:
            logger.error("load04_func is not defined.")
            sys.exit(1)
        self.__load04_func: Optional[Callable[[float], float]] = load04_func

    # テスト用の公開プロパティ

    @property
    def previous_size(self):
        return self.__previous_size

    @previous_size.setter
    def previous_size(self, previous_size: int):
        self.__previous_size = previous_size

    @property
    def previous_df_tail(self):
        return self.__previous_df_tail

    @previous_df_tail.setter
    def previous_df_tail(self, previous_df_tail: DataFrame):
        self.__previous_df_tail = previous_df_tail

    @property
    def min_spm(self):
        return self.__min_spm

    @min_spm.setter
    def min_spm(self, min_spm: int):
        self.__min_spm = min_spm

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
    def margin(self):
        return self.__margin

    @margin.setter
    def margin(self, margin: float):
        self.__margin = margin

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

    @property
    def shots_meta_df(self):
        return self.__shots_meta_df

    @shots_meta_df.setter
    def shots_meta_df(self, shots_meta_df: DataFrame):
        self.__shots_meta_df = shots_meta_df

    def _get_collect_start_time(self, events: List[dict]) -> Optional[float]:
        """ events_indexから収集開始時間を取得 """

        start_events: List[dict] = [x for x in events if x["event_type"] == "start"]

        if len(start_events) == 0:
            logger.error("Data collection has not started yet.")
            sys.exit(1)

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

    def _get_pickle_list(self, rawdata_dir_path: str) -> List[str]:
        """ 取り込むファイルのリストを取得する """

        pickle_file_list: List[str] = glob.glob(os.path.join(rawdata_dir_path, "*.pkl"))
        pickle_file_list.sort()

        return pickle_file_list

    def _exclude_non_target_interval(
        self, df: DataFrame, start_sequential_number: int, end_sequential_number: int
    ) -> DataFrame:
        """ パラメータで指定された対象範囲に含まれないデータを除外 """

        return df[
            (start_sequential_number <= df["sequential_number"]) & (df["sequential_number"] <= end_sequential_number)
        ]

    def _exclude_setup_interval(self, df: DataFrame, collect_start_time: float) -> DataFrame:
        """ 収集開始前(段取中)のデータを除外 """

        return df[df["timestamp"] >= collect_start_time]

    def _exclude_pause_interval(self, df: DataFrame, pause_events: List[dict]) -> DataFrame:
        """ 中断区間のデータを除外 """

        for pause_event in pause_events:
            df = df[(df["timestamp"] < pause_event["start_time"]) | (pause_event["end_time"] < df["timestamp"])]

        return df

    def _detect_shot_start(self, displacement: float, start_displacement: float, end_displacement: float) -> bool:
        """ ショット開始検知。ショットが未検出かつ変位値が終了しきい値以上開始しきい値以下の場合、ショット開始とみなす。 """

        return (not self.__is_shot_section) and (end_displacement <= displacement <= start_displacement)

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
        self.__previous_df_tail = df[-N:].copy()

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
        start_index = row_number
        end_index = row_number
        return pd.concat([self.__previous_df_tail[start_index:], rawdata_df[:end_index]], axis=0)

    def _calculate_spm(self, timestamp: float) -> Optional[float]:
        """ spm (shot per minute) 計算。ショット検出時、前ショットの開始時間との差分を計算する。 """

        if self.__previous_shot_start_time is None:
            logger.error("Invalid process. previous_shot_start_time is None.")
            sys.exit(1)

        try:
            # NOTE: 小数点以下計算に誤差があるため、下2桁で丸め
            spm: Optional[float] = 60.0 / round((timestamp - self.__previous_shot_start_time), 2)
        except ZeroDivisionError:
            logger.error(f"ZeroDivisionError. shot_number: {self.__shot_number}")
            spm = None

        logger.debug(f"shot_number: {self.__shot_number}, spm: {spm}")

        return spm

    def _initialize_when_shot_detected(self) -> None:
        """ ショット検出時の初期処理 """

        self.__is_shot_section = True
        self.__is_target_of_cut_out = True  # ショット開始 = 切り出し区間開始
        self.__shot_number += 1
        self.__sequential_number_by_shot = 0

    def _include_previous_data(self, preceding_df: DataFrame) -> None:
        """ ショット検出時、previous_size分のデータを遡って切り出し対象に含める。荷重立ち上がり点取りこぼし防止のため。 """

        for row in preceding_df.itertuples():
            self._add_cut_out_target(row)

    def _add_cut_out_target(self, rawdata) -> None:
        """ 切り出し対象としてデータを追加 """

        cut_out_target: dict = {
            "timestamp": rawdata.timestamp,
            "sequential_number": self.__sequential_number,
            "sequential_number_by_shot": self.__sequential_number_by_shot,
            "rawdata_sequential_number": int(rawdata.sequential_number),
            "displacement": rawdata.displacement,
            "load01": rawdata.load01,
            "load02": rawdata.load02,
            "load03": rawdata.load03,
            "load04": rawdata.load04,
            "shot_number": self.__shot_number,
            "tags": [],
        }
        self.__cut_out_targets.append(cut_out_target)
        self.__sequential_number += 1
        self.__sequential_number_by_shot += 1

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

        logger.debug(f"over_sample_shot detected. shot_numbers: {over_sample_shot_numbers}")

        return df.query("shot_number not in @over_sample_shot_numbers")

    def _apply_expr_displacement(self, df: DataFrame) -> DataFrame:
        """ 変位値に対して変換式を適用 """

        # NOTE: SettingWithCopyWarning回避のため、locで指定して代入
        df.loc[:, "displacement"] = df["displacement"].apply(self.__displacement_func)

        return df

    def _apply_expr_load(self, df: DataFrame) -> DataFrame:
        """ 荷重値に対して変換式を適用 """

        # NOTE: SettingWithCopyWarning回避のため、locで指定して代入
        df.loc[:, "load01"] = df["load01"].apply(self.__load01_func)
        df.loc[:, "load02"] = df["load02"].apply(self.__load02_func)
        df.loc[:, "load03"] = df["load03"].apply(self.__load03_func)
        df.loc[:, "load04"] = df["load04"].apply(self.__load04_func)

        return df

    def _export_shots_meta_to_es(self, shots_meta_index: str) -> None:
        """ ショットメタデータをshots_metaインデックスに出力 """

        if self.__previous_shot_start_time is None:
            logger.error("self.__previous_shot_start_time should not be None.")
            sys.exit(1)

        # 最後のショットのメタデータを追加
        d: dict = {
            "timestamp": datetime.fromtimestamp(self.__previous_shot_start_time),
            "shot_number": self.__shot_number,
            "spm": None,
            "num_of_samples_in_cut_out": self.__sequential_number_by_shot,
        }
        self.__shots_meta_df = self.__shots_meta_df.append(d, ignore_index=True)
        self.__shots_meta_df["spm"] = self.__shots_meta_df["spm"].where(self.__shots_meta_df["spm"].notna(), None)

        self.__shots_meta_df = self.__shots_meta_df.astype({"shot_number": int, "num_of_samples_in_cut_out": int})

        shots_meta_data: List[dict] = self.__shots_meta_df.to_dict(orient="records")

        ElasticManager.bulk_insert(shots_meta_data, shots_meta_index)

    def __join_process(self, procs: List[multiprocessing.context.Process]) -> List:
        """ マルチプロセスの処理待ち """

        if len(procs) > 0:
            for p in procs:
                p.join()

        return []

    def _set_start_sequential_number(self, start_sequential_number: Optional[int], rawdata_count: int) -> int:
        """ パラメータ start_sequential_number の設定 """

        if start_sequential_number is None:
            return 0

        if start_sequential_number >= rawdata_count:
            logger.error(
                f"start_sequential_number: {start_sequential_number} must be less than rawdata count ({rawdata_count})"
            )
            sys.exit(1)

        if start_sequential_number < 0:
            logger.error(f"start_sequential_number: {start_sequential_number} must be greater than 0")
            sys.exit(1)

        return start_sequential_number

    def _set_end_sequential_number(
        self, start_sequential_number: Optional[int], end_sequential_number: Optional[int], rawdata_count: int
    ) -> int:
        """ パラメータ end_sequential_number の設定 """

        if start_sequential_number is None:
            logger.error("start_sequential_number should not be None.")
            sys.exit(1)

        if end_sequential_number is None:
            return rawdata_count

        if end_sequential_number >= rawdata_count:
            logger.error(
                f"end_sequential_number: {end_sequential_number} must be less than rawdata count ({rawdata_count})"
            )
            sys.exit(1)

        if end_sequential_number <= 0:
            logger.error(f"end_sequential_number: {end_sequential_number} must be greater than equal 0")
            sys.exit(1)

        if end_sequential_number <= start_sequential_number:
            logger.error(
                f"end_sequential_number: {end_sequential_number} must be greater than equal start_sequential_number ({start_sequential_number})"
            )
            sys.exit(1)

        return end_sequential_number

    def cut_out_shot(
        self,
        rawdata_dir_name: str,
        start_displacement: float,
        end_displacement: float,
        start_sequential_number: Optional[int] = None,
        end_sequential_number: Optional[int] = None,
    ) -> None:
        """
        * ショット切り出し
        * 中断区間のデータ除外
        * 物理変換 + 校正
        * SPM計算
        * 事象記録のタグ付け
        * SPMから算出される、ショット当たりの最大サンプル数を超えたショット除外
        * Elasticsearchインデックスへの保存
        * shots-yyyyMMddHHMMSS-data：切り出されたショットデータ
        * shots-yyyyMMddHHMMSS-meta：ショットのメタデータ

        Args:
            rawdata_filename: 生データcsvのファイル名
            start_displacement: ショット開始となる変位値
            end_displacement: ショット終了となる変位値
        """

        logger.info("Cut out shot start.")

        if start_displacement <= end_displacement:
            logger.error("start_displacement must be greater than end_displacement.")
            sys.exit(1)

        # 取り込むpickleファイルのリストを取得
        data_dir: str = common.get_config_value(common.APP_CONFIG_PATH, "data_dir")
        rawdata_dir_path: str = os.path.join(data_dir, rawdata_dir_name)

        if not os.path.exists(rawdata_dir_path):
            logger.error(f"Directory not found. {rawdata_dir_path}")
            sys.exit(1)

        pickle_files: List[str] = self._get_pickle_list(rawdata_dir_path)

        # パラメータによる範囲フィルター設定
        if start_sequential_number is not None or end_sequential_number is not None:
            has_target_interval: bool = True
            rawdata_index: str = "rawdata-" + rawdata_dir_name
            rawdata_count: int = ElasticManager.count(index=rawdata_index)
            start_sequential_number = self._set_start_sequential_number(start_sequential_number, rawdata_count)
            end_sequential_number = self._set_end_sequential_number(
                start_sequential_number, end_sequential_number, rawdata_count
            )
        else:
            has_target_interval = False

        shots_index: str = "shots-" + rawdata_dir_name + "-data"
        ElasticManager.delete_exists_index(index=shots_index)
        mapping_shots: str = common.get_config_value(common.APP_CONFIG_PATH, "mapping_shots_path")
        setting_shots: str = common.get_config_value(common.APP_CONFIG_PATH, "setting_shots_path")
        ElasticManager.create_index(index=shots_index, mapping_file=mapping_shots, setting_file=setting_shots)

        shots_meta_index: str = "shots-" + rawdata_dir_name + "-meta"
        ElasticManager.delete_exists_index(index=shots_meta_index)
        mapping_shots_meta: str = common.get_config_value(common.APP_CONFIG_PATH, "mapping_shots_meta_path")
        setting_shots_meta: str = common.get_config_value(common.APP_CONFIG_PATH, "setting_shots_meta_path")
        ElasticManager.create_index(
            index=shots_meta_index, mapping_file=mapping_shots_meta, setting_file=setting_shots_meta
        )

        # event_indexから各種イベント情報を取得する
        events_index: str = "events-" + rawdata_dir_name
        query: dict = {"sort": {"event_id": {"order": "asc"}}}
        events: List[dict] = ElasticManager.get_docs(index=events_index, query=query)

        if len(events) == 0:
            logger.error("Exits because no events.")
            return

        # 最後のイベントが記録済み(recorded)であることが前提
        if events[-1]["event_type"] != "recorded":
            logger.error("Exits because the status is not recorded.")
            return

        collect_start_time: Optional[float] = self._get_collect_start_time(events)
        if collect_start_time is None:
            logger.error("Exits because collect time is not recorded.")
            return

        pause_events: List[dict] = self._get_pause_events(events)
        # tag_events: List[dict] = self._get_tag_events(events)

        procs: List[multiprocessing.context.Process] = []
        processed_count: int = 0

        NOW: Final[datetime] = datetime.now()

        # main loop
        for loop_count, pickle_file in enumerate(pickle_files):
            rawdata_df: DataFrame = pd.read_pickle(pickle_file)

            # パラメータで指定された対象範囲に含まれないデータを除外
            if has_target_interval:
                if start_sequential_number is None:
                    logger.error("start_sequential_number should not be None.")
                    sys.exit(1)
                if end_sequential_number is None:
                    logger.error("end_sequential_number should not be None.")
                    sys.exit(1)
                rawdata_df = self._exclude_non_target_interval(
                    rawdata_df, start_sequential_number, end_sequential_number
                )

            if len(rawdata_df) == 0:
                logger.info(f"All data was excluded by non-target interval. {pickle_file}")
                continue

            # 段取区間の除外
            rawdata_df = self._exclude_setup_interval(rawdata_df, collect_start_time)

            if len(rawdata_df) == 0:
                logger.info(f"All data was excluded by setup interval. {pickle_file}")
                continue

            # 中断区間の除外
            if len(pause_events) > 0:
                rawdata_df = self._exclude_pause_interval(rawdata_df, pause_events)

            if len(rawdata_df) == 0:
                logger.info(f"All data was excluded by pause interval. {pickle_file}")
                # self.__previous_df_tailを空にしておく
                self._backup_df_tail(rawdata_df)
                continue

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
            cut_out_df = self._exclude_over_sample(cut_out_df)

            if len(cut_out_df) == 0:
                logger.info(f"Shot is not detected in {pickle_file} by over_sample_filter.")
                continue

            # 荷重値に変換式を適用
            cut_out_df = self._apply_expr_load(cut_out_df)

            # タグ付け
            tm = TagManager(back_seconds_for_tagging=self.__back_seconds_for_tagging)
            cut_out_df = tm.tagging(cut_out_df, events)

            # timestampをdatetimeに変換する
            cut_out_df["timestamp"] = cut_out_df["timestamp"].apply(lambda x: datetime.fromtimestamp(x))

            # Elasticsearchに格納するため、dictに戻す
            self.__cut_out_targets = cut_out_df.to_dict(orient="records")

            logger.info(f"{len(self.__cut_out_targets)} data cut out from {pickle_file}.")

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

        logger.info("Cut out shot finished.")

    def _cut_out_shot(self, rawdata_df: DataFrame, start_displacement: float, end_displacement: float):
        """ ショット切り出し処理。生データの変位値を参照し、ショット対象となるデータのみをリストに含めて返す。 """

        for row_number, rawdata in enumerate(rawdata_df.itertuples()):
            if self._detect_shot_start(rawdata.displacement, start_displacement, end_displacement):
                if self.__shot_number == 0:
                    self.__previous_shot_start_time = rawdata.timestamp
                # 2つめ以降のショット検知時は、1つ前のショットのspmを計算して記録する
                else:
                    spm: Optional[float] = self._calculate_spm(rawdata.timestamp)

                    if self.__previous_shot_start_time is None:
                        logger.error("self.__previous_shot_start_time should not be None.")
                        sys.exit(1)

                    self.__shots_meta_df = self.__shots_meta_df.append(
                        {
                            "timestamp": datetime.fromtimestamp(self.__previous_shot_start_time),
                            "shot_number": self.__shot_number,
                            "spm": spm,
                            "num_of_samples_in_cut_out": self.__sequential_number_by_shot,
                        },
                        ignore_index=True,
                    )
                    self.__previous_shot_start_time = rawdata.timestamp

                self._initialize_when_shot_detected()

                # 荷重開始点取りこぼし防止
                preceding_df: DataFrame = self._get_preceding_df(row_number, rawdata_df)
                if len(preceding_df) != 0:
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


if __name__ == "__main__":
    LOG_FILE: Final[str] = os.path.join(
        common.get_config_value(common.APP_CONFIG_PATH, "log_dir"), "cut_out_shot/cut_out_shot.log"
    )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.handlers.RotatingFileHandler(
                LOG_FILE, maxBytes=common.MAX_LOG_SIZE, backupCount=common.BACKUP_COUNT
            ),
            logging.StreamHandler(),
        ],
    )

    # # 変位値変換 距離(mm) = 70.0 - (v - 2.0) * 70.0 / 8.0
    # displacement_func = lambda v: 70.0 - (v - 2.0) * 70.0 / 8.0

    # # 荷重値換算
    # Vr = 2.5
    # load01_func = lambda v: 2.5 / Vr * v
    # load02_func = lambda v: 2.5 / Vr * v
    # load03_func = lambda v: 2.5 / Vr * v
    # load04_func = lambda v: 2.5 / Vr * v

    displacement_func = lambda v: v
    Vr = 2.5
    load01_func = lambda v: 2.5 / Vr * v
    load02_func = lambda v: 2.5 / Vr * v
    load03_func = lambda v: 2.5 / Vr * v
    load04_func = lambda v: 2.5 / Vr * v

    cut_out_shot = CutOutShot(
        displacement_func=displacement_func,
        load01_func=load01_func,
        load02_func=load02_func,
        load03_func=load03_func,
        load04_func=load04_func,
        previous_size=5,
        margin=0.01,
    )
    cut_out_shot.cut_out_shot(rawdata_dir_name="20210101000000", start_displacement=150.0, end_displacement=25.0)

    # cut_out_shot = CutOutShot(
    #     min_spm=15,
    #     back_seconds_for_tagging=120,
    #     previous_size=1_000,
    #     chunk_size=5_000,
    #     margin=0.3,
    #     displacement_func=displacement_func,
    #     load01_func=load01_func,
    #     load02_func=load02_func,
    #     load03_func=load03_func,
    #     load04_func=load04_func,
    # )
    # cut_out_shot.cut_out_shot(rawdata_dir_name="20210327141514", start_displacement=47.0, end_displacement=34.0)
