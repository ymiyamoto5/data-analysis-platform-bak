"""
 ==================================
  analyzer.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import warnings

warnings.simplefilter("ignore")
import multiprocessing
import sys
import traceback
import pandas as pd
from typing import Callable, List, Tuple, Optional
from pandas.core.frame import DataFrame
import backend.analyzer.h_one_extract_features as ef
from backend.elastic_manager.elastic_manager import ElasticManager
from backend.data_reader.data_reader import DataReader
from backend.common import common
from backend.common.common_logger import logger


class Analyzer:
    def __init__(
        self, target: str, shots_df: DataFrame, shots_meta_df: DataFrame, exclude_shots: Optional[Tuple[int, ...]]
    ):
        self.__target = target
        self.__shots_df = shots_df
        self.__shots_meta_df = shots_meta_df
        self.__exclude_shots = exclude_shots

    def apply(
        self,
        feature: str,
        func: Callable,
        sub_func: Callable = None,
    ) -> None:
        """特定のロジックを3,000ショットに適用"""

        logger.info("apply start.")

        if feature not in ("max", "start", "break"):
            logger.error(f"feature: {feature} is invalid.")
            sys.exit(1)

        feature_index: str = "shots-" + self.__target + "-" + feature + "-point"
        ElasticManager.delete_exists_index(index=feature_index)

        # NOTE: データをNショット毎に分割/ロジック適用/ELS保存。並列処理の関係上1メソッドにまとめた。
        self._multi_process(feature_index, feature, func, sub_func)

        logger.info("apply finished.")

    def _multi_process(
        self,
        feature_index: str,
        feature: str,
        func: Callable,
        sub_func: Callable = None,
    ) -> None:
        """データを複数ショット単位で読み込み、ロジック適用、ELS格納"""

        # NOTE: ショットを削除した場合ショット番号が歯抜けになるため、countではなく最終ショット番号を採用
        num_of_shots: int = self.__shots_meta_df.shot_number.iloc[-1]

        # データをプロセッサの数に均等分配
        shots_num_by_proc: List[int] = [
            (num_of_shots + i) // common.NUM_OF_PROCESS for i in range(common.NUM_OF_PROCESS)
        ]
        logger.debug(f"shots_num_by_proc: {shots_num_by_proc}")

        procs: List[multiprocessing.context.Process] = []
        start_shot_number: int = 1
        # Nショット分をまとめてプロセスに割当。
        for shots_num in shots_num_by_proc:
            logger.debug(f"start_shot_number: {start_shot_number}")
            end_shot_number: int = start_shot_number + shots_num
            logger.debug(f"end_shot_number: {end_shot_number}")

            proc: multiprocessing.context.Process = multiprocessing.Process(
                target=self._apply_logic,
                args=(
                    feature_index,
                    start_shot_number,
                    end_shot_number,
                    feature,
                    func,
                    sub_func,
                ),
            )
            proc.start()
            procs.append(proc)

            start_shot_number = end_shot_number

        for proc in procs:
            proc.join()

    def _apply_logic(
        self,
        feature_index: str,
        start_shot_number: int,
        end_shot_number: int,
        feature: str,
        func: Callable,
        sub_func: Callable = None,
    ) -> None:
        """ショットに対しロジック(func)適用"""

        result: List[dict] = []

        for shot_number in range(start_shot_number, end_shot_number):
            # 除外ショットはスキップ
            if self.__exclude_shots is not None:
                if shot_number in self.__exclude_shots:
                    logger.info(f"shot_number: {shot_number} was excluded.")
                    continue

            # 特定ショット番号のデータを抽出
            shot_df: DataFrame = self.__shots_df[self.__shots_df.shot_number == shot_number]

            if len(shot_df) == 0:
                logger.info(f"shot_number: {shot_number} was not found.")
                continue

            shot_df = shot_df.reset_index()

            spm: Optional[float] = self.__shots_meta_df[self.__shots_meta_df.shot_number == shot_number].spm
            # TODO: 後続エラー回避のため、暫定対処としてNoneのときは80.0としている
            spm = float(spm) if spm.iloc[0] is not None else 80.0  # type: ignore

            indices: List[int]
            values: List[float]
            debug_values: List[float]
            # ロジック適用
            try:
                indices, values, debug_values = ef.extract_features(shot_df, spm, func, sub_func=sub_func)
            except Exception:
                logger.error(f"Failed to apply logic. shot_number: {shot_number}. \n{traceback.format_exc()}")
                continue

            if feature == "break":
                break_channels: Tuple[str, str] = self._extract_break_channels(values)

            # 荷重センサー毎にdict化
            for i in range(0, common.NUM_OF_LOAD_SENSOR):
                d: dict = {
                    "timestamp": shot_df.iloc[indices[i]].timestamp,
                    "shot_number": shot_number,
                    "load": "load0" + str(i + 1),
                    "sequential_number": shot_df.iloc[indices[i]].sequential_number,
                    "sequential_number_by_shot": indices[i],
                    "value": values[i],
                }

                if feature == "break":
                    d["break_channels"] = break_channels

                result.append(d)

        # ELSに保存
        ElasticManager.bulk_insert(result, feature_index)

    def _extract_break_channels(self, values: List[float]) -> Tuple[str, str]:
        """4ch分の破断点の荷重値リストを受け取り、破断側のチャネルセットを返す。"""

        min_index = values.index(min(values))

        # 最小値のindex = 0 or 1 のとき、ch01, ch02が破断側
        if min_index in (0, 1):
            return ("load01", "load02")
        # 最小値のindex = 2 or 3 のとき、ch03, ch04が破断側
        else:
            return ("load03", "load04")

    def start_break_diff(self, start_df: DataFrame, break_df: DataFrame) -> DataFrame:
        """荷重開始と破断開始の時刻の差分を計算してELSに保存する。"""
        # shot_numberとloadをkeyにmerge
        start_break_df: DataFrame = DataFrame.merge(
            start_df,
            break_df,
            on=["shot_number", "load"],
            suffixes=("_start", "_break"),
        )
        # 除外ショットの削除
        if self.__exclude_shots is not None:
            for i in self.__exclude_shots:
                start_break_df = start_break_df.drop(start_break_df.index[start_break_df["shot_number"] == i])
        # 荷重開始と破断開始の時刻の差分を計算
        start_break_df["diff"] = pd.to_datetime(start_break_df["timestamp_break"]).map(
            pd.Timestamp.timestamp
        ) - pd.to_datetime(start_break_df["timestamp_start"]).map(pd.Timestamp.timestamp)
        # 必要な列を選択
        diff_df: DataFrame = DataFrame(data=start_break_df[["timestamp_start", "shot_number", "load", "diff"]])
        diff_df.rename(columns={"timestamp_start": "timestamp"}, inplace=True)

        # 荷重センサー毎にdict化
        result: List[dict] = diff_df.to_dict(orient="records")

        # 既存のインデックスを削除する
        feature_index: str = "shots-" + self.__target + "-start-break-diff"
        ElasticManager.delete_exists_index(index=feature_index)

        # ELSに保存
        ElasticManager.bulk_insert(result, feature_index)

        return diff_df


if __name__ == "__main__":
    # target = "20210327141514"
    target = "20210708113000"
    shots_data_index = "shots-" + target + "-data"
    shots_meta_index = "shots-" + target + "-meta"

    dr = DataReader()
    shots_df: DataFrame = dr.multi_process_read_all(shots_data_index)
    shots_meta_df = dr.read_shots_meta(shots_meta_index)

    # exclude_shots: Optional[Tuple[int, ...]] = (983, 1227, 1228, 1229, 1369, 1381)
    exclude_shots: Optional[Tuple[int]] = None

    analyzer = Analyzer(target, shots_df, shots_meta_df, exclude_shots)
    analyzer.apply(
        feature="max",
        func=ef.max_load,
        sub_func=None,
    )
    analyzer.apply(
        feature="start",
        func=ef.load_start3,
        sub_func=None,
    )
    analyzer.apply(
        feature="break",
        func=ef.breaking_vmin_amin,
        sub_func=ef.narrowing_v4min_mab,
    )

    start_index = "shots-" + target + "-start-point"
    start_df = dr.read_all(start_index)
    break_index = "shots-" + target + "-break-point"
    break_df = dr.read_all(break_index)
    analyzer.start_break_diff(start_df=start_df, break_df=break_df)
