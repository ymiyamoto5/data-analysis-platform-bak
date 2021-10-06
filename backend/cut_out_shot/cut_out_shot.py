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
import traceback
from datetime import datetime
from typing import Any, Callable, Dict, Final, List, Optional, Union

import numpy as np
import pandas as pd
from backend.app.models.data_collect_history_detail import DataCollectHistoryDetail
from backend.common import common
from backend.common.common_logger import logger
from backend.data_converter.data_converter import DataConverter
from backend.elastic_manager.elastic_manager import ElasticManager
from backend.event_manager.event_manager import EventManager
from backend.file_manager.file_manager import FileManager
from backend.tag_manager.tag_manager import TagManager
from backend.utils.throughput_counter import throughput_counter
from pandas.core.frame import DataFrame

from .displacement_cutter import DisplacementCutter
from .pulse_cutter import PulseCutter


class CutOutShot:
    def __init__(
        self,
        cutter: Union[DisplacementCutter, PulseCutter],
        sensors: List[DataCollectHistoryDetail],
        sampling_frequency: int,
        machine_id: str,
        target: str,  # yyyyMMddhhmmss文字列
        min_spm: int = 15,
        back_seconds_for_tagging: int = 120,
        num_of_process: int = common.NUM_OF_PROCESS,
        chunk_size: int = 5_000,
    ):
        self.__machine_id = machine_id
        self.__rawdata_dir_name = machine_id + "-" + target
        self.__min_spm: int = min_spm
        self.__back_seconds_for_tagging: int = back_seconds_for_tagging
        self.__num_of_process: int = num_of_process
        self.__chunk_size: int = chunk_size
        self.__shots_meta_df: DataFrame = pd.DataFrame(
            columns=("timestamp", "shot_number", "spm", "num_of_samples_in_cut_out")
        )
        self.__sensors: List[DataCollectHistoryDetail] = sensors
        self.__max_samples_per_shot: int = int(60 / self.__min_spm) * sampling_frequency
        self.cutter: Union[DisplacementCutter, PulseCutter] = cutter

    # テスト用の公開プロパティ
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
    def shots_meta_df(self):
        return self.__shots_meta_df

    @shots_meta_df.setter
    def shots_meta_df(self, shots_meta_df: DataFrame):
        self.__shots_meta_df = shots_meta_df

    @staticmethod
    def _exclude_non_target_interval(
        df: DataFrame, start_sequential_number: int, end_sequential_number: int
    ) -> DataFrame:
        """パラメータで指定された対象範囲に含まれないデータを除外"""

        return df[
            (start_sequential_number <= df["sequential_number"]) & (df["sequential_number"] <= end_sequential_number)
        ]

    @staticmethod
    def _exclude_setup_interval(df: DataFrame, collect_start_time: float) -> DataFrame:
        """収集開始前(段取中)のデータを除外"""

        return df[df["timestamp"] >= collect_start_time]

    @staticmethod
    def _exclude_pause_interval(df: DataFrame, pause_events: List[dict]) -> DataFrame:
        """中断区間のデータを除外"""

        for pause_event in pause_events:
            df = df[(df["timestamp"] < pause_event["start_time"]) | (pause_event["end_time"] < df["timestamp"])]

        return df

    def _set_to_none_for_low_spm(self) -> DataFrame:
        """切り出したショットの内、最低spmを下回るショットのspmはNoneに設定する"""

        self.__shots_meta_df["spm"] = self.__shots_meta_df["spm"].where(
            self.__shots_meta_df["spm"] >= self.__min_spm, np.nan
        )

    def _exclude_over_sample(self, df: DataFrame) -> DataFrame:
        """切り出したショットの内、最大サンプル数を上回るショットを除外したDataFrameを返す"""

        over_sample_df: DataFrame = self.__shots_meta_df[
            self.__shots_meta_df["num_of_samples_in_cut_out"] > self.__max_samples_per_shot
        ]

        if len(over_sample_df) == 0:
            return df

        over_sample_shot_numbers: List[float] = list(over_sample_df.shot_number)

        logger.debug(f"over_sample_shot detected. shot_numbers: {over_sample_shot_numbers}")

        return df.query("shot_number not in @over_sample_shot_numbers")

    def _apply_physical_conversion_formula(self, df: DataFrame) -> DataFrame:
        """荷重値に対して変換式を適用"""

        for sensor in self.__sensors:
            func: Callable[[float], float] = DataConverter.get_physical_conversion_formula(sensor)
            # NOTE: SettingWithCopyWarning回避のため、locで指定して代入
            df.loc[:, sensor.sensor_id] = df[sensor.sensor_id].map(func)

        return df

    def _create_shots_meta_df(self, shots_summary: List[Dict[str, Any]]) -> None:
        """ショットのサマリ情報からショットメタデータDataFrameを作成する"""

        shots_summary_df: DataFrame = pd.DataFrame(shots_summary)
        # ショット間時刻差分
        shots_summary_df["diff"] = shots_summary_df["timestamp"].diff().shift(-1)

        try:
            shots_summary_df["spm"] = round(60.0 / shots_summary_df["diff"], 2)
        except ZeroDivisionError:
            logger.error(traceback.format_exc())

        self.__shots_meta_df = shots_summary_df.drop(columns=["diff"])

    def _export_shots_meta_to_es(self, shots_meta_index: str) -> None:
        """ショットメタデータをshots_metaインデックスに出力"""

        self.__shots_meta_df.replace(dict(spm={np.nan: None}), inplace=True)
        self.__shots_meta_df["timestamp"] = self.__shots_meta_df["timestamp"].map(lambda x: datetime.fromtimestamp(x))

        shots_meta_data: List[dict] = self.__shots_meta_df.to_dict(orient="records")

        ElasticManager.bulk_insert(shots_meta_data, shots_meta_index)

    @staticmethod
    def __join_process(procs: List[multiprocessing.context.Process]) -> List:
        """マルチプロセスの処理待ち"""

        if len(procs) > 0:
            for p in procs:
                p.join()

        return []

    @staticmethod
    def _set_start_sequential_number(start_sequential_number: Optional[int], rawdata_count: int) -> int:
        """パラメータ start_sequential_number の設定"""

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

    @staticmethod
    def _set_end_sequential_number(
        start_sequential_number: Optional[int], end_sequential_number: Optional[int], rawdata_count: int
    ) -> int:
        """パラメータ end_sequential_number の設定"""

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
                f"end_sequential_number: {end_sequential_number} must be greater than equal start_sequential_number ({start_sequential_number})"  # noqa
            )
            sys.exit(1)

        return end_sequential_number

    def cut_out_shot(
        self,
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
            start_sequential_number: 開始位置
            end_sequential_number: 終了位置
        """

        logger.info("Cut out shot start.")

        # 取り込むpickleファイルのリストを取得
        data_dir: str = common.get_config_value(common.APP_CONFIG_PATH, "data_dir")
        rawdata_dir_path: str = os.path.join(data_dir, self.__rawdata_dir_name)

        if not os.path.exists(rawdata_dir_path):
            logger.error(f"Directory not found. {rawdata_dir_path}")
            sys.exit(1)

        pickle_files: List[str] = FileManager.get_files(
            dir_path=rawdata_dir_path, pattern=f"{self.__machine_id}_*.pkl"
        )

        if len(pickle_files) == 0:
            logger.error("pickle files not found.")
            sys.exit(1)

        # パラメータによる範囲フィルター設定
        if start_sequential_number is not None or end_sequential_number is not None:
            has_target_interval: bool = True
            rawdata_index: str = self.__machine_id + "-rawdata-" + self.__rawdata_dir_name
            rawdata_count: int = ElasticManager.count(index=rawdata_index)
            start_sequential_number = self._set_start_sequential_number(start_sequential_number, rawdata_count)
            end_sequential_number = self._set_end_sequential_number(
                start_sequential_number, end_sequential_number, rawdata_count
            )
        else:
            has_target_interval = False

        shots_index: str = "shots-" + self.__rawdata_dir_name + "-data"
        ElasticManager.delete_exists_index(index=shots_index)
        setting_shots: str = common.get_config_value(common.APP_CONFIG_PATH, "setting_shots_path")
        ElasticManager.create_index(index=shots_index, setting_file=setting_shots)

        shots_meta_index: str = "shots-" + self.__rawdata_dir_name + "-meta"
        ElasticManager.delete_exists_index(index=shots_meta_index)
        setting_shots_meta: str = common.get_config_value(common.APP_CONFIG_PATH, "setting_shots_meta_path")
        ElasticManager.create_index(index=shots_meta_index, setting_file=setting_shots_meta)

        # event_indexから各種イベント情報を取得する
        events_index: str = "events-" + self.__rawdata_dir_name
        events: List[dict] = EventManager.fetch_events(events_index)

        if len(events) == 0:
            logger.error("Exits because no events.")
            return

        # 最後のイベントが記録済み(recorded)であることが前提
        if events[-1]["event_type"] != common.COLLECT_STATUS.RECORDED.value:
            logger.error("Exits because the status is not recorded.")
            return

        collect_start_time: Optional[float] = EventManager.get_collect_start_time(events)
        if collect_start_time is None:
            logger.error("Exits because collect time is not recorded.")
            return

        pause_events: List[dict] = EventManager.get_pause_events(events)

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
                continue

            # NOTE: 変換式適用.パフォーマンス的には変位値のみ変換し、切り出し後に荷重値を変換したほうがよい。
            # コードのシンプルさを優先し、全列まとめて物理変換している。
            rawdata_df = self._apply_physical_conversion_formula(rawdata_df)

            # ショット切り出し
            self.cutter.cut_out_shot(rawdata_df)

            # スループット表示
            if loop_count != 0:
                processed_count += len(rawdata_df)
                throughput_counter(processed_count, NOW)

            # ショットがなければ以降の処理はスキップ
            if len(self.cutter.cut_out_targets) == 0:
                logger.info(f"Shot is not detected in {pickle_file}")
                continue

            # NOTE: 以下処理のため一時的にDataFrameに変換している。
            cut_out_df: DataFrame = pd.DataFrame(self.cutter.cut_out_targets)
            # cutter.cut_out_targetは以降使わないためクリア
            self.cutter.cut_out_targets = []

            # 最大サンプル数を超えたショットの削除
            cut_out_df = self._exclude_over_sample(cut_out_df)

            if len(cut_out_df) == 0:
                logger.info(f"Shot is not detected in {pickle_file} by over_sample_filter.")
                continue

            # タグ付け
            tm = TagManager(back_seconds_for_tagging=self.__back_seconds_for_tagging)
            cut_out_df = tm.tagging(cut_out_df, events)

            # timestampをdatetimeに変換する
            cut_out_df["timestamp"] = cut_out_df["timestamp"].map(lambda x: datetime.fromtimestamp(x))

            # Elasticsearchに格納するため、dictに戻す
            cut_out_targets = cut_out_df.to_dict(orient="records")

            # 子プロセスのjoin
            procs = self.__join_process(procs)

            # Elasticsearchに出力
            procs = ElasticManager.multi_process_bulk_lazy_join(
                data=cut_out_targets,
                index_to_import=shots_index,
                num_of_process=self.__num_of_process,
                chunk_size=self.__chunk_size,
            )

            cut_out_targets = []

        # 全ファイル走査後、子プロセスが残っていればjoin
        procs = self.__join_process(procs)

        # ショットメタデータDF作成
        self._create_shots_meta_df(self.cutter.shots_summary)

        # spmがしきい値以下の場合、Noneとする。
        self._set_to_none_for_low_spm()

        # ショットメタデータをElasticsearchに出力
        self._export_shots_meta_to_es(shots_meta_index)

        logger.info("Cut out shot finished.")


if __name__ == "__main__":
    from backend.app.crud.crud_data_collect_history import CRUDDataCollectHistory  # noqa
    from backend.app.db.session import SessionLocal  # noqa

    machine_id: str = "machine-01"
    target: str = "20210327141514"
    db = SessionLocal()
    history = CRUDDataCollectHistory.select_by_machine_id_started_at(db, machine_id, target)

    cutter = DisplacementCutter(
        start_displacement=47.0, end_displacement=34.0, margin=0.3, sensors=history.data_collect_history_details
    )

    cut_out_shot = CutOutShot(
        cutter=cutter,
        machine_id=machine_id,
        target=target,
        min_spm=15,
        back_seconds_for_tagging=120,
        sampling_frequency=history.sampling_frequency,
        sensors=history.data_collect_history_details,
    )

    cut_out_shot.cut_out_shot()
