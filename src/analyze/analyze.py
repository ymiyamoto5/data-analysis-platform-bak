import warnings

warnings.simplefilter("ignore")
import multiprocessing
import os
import sys
import logging
import logging.handlers
import pandas as pd
from typing import Callable, Final, List, Optional, Tuple
from pandas.core.frame import DataFrame

import h_one_extract_features as ef

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from elastic_manager.elastic_manager import ElasticManager
from data_reader.data_reader import DataReader

sys.path.append(os.path.join(os.path.dirname(__file__), "../utils"))
from time_logger import time_log
from throughput_counter import throughput_counter
import common

logger = logging.getLogger(__name__)


def apply(target: str, feature: str, func: Callable, sub_func: Callable):
    """ 特定のロジックを3,000ショットに適用 """

    logger.info("apply start.")

    if feature not in ("max", "start", "break"):
        logger.error(f"feature: {feature} is invalid.")
        SystemExit()

    sub_func: Optional[Callable] = None if feature != "break" else sub_func

    feature_index: str = "shots-" + target + "-" + feature + "-point"
    ElasticManager.delete_exists_index(index=feature_index)

    # NOTE: データ分割をNショット毎に分割/ロジック適用/ELS保存。並列処理の関係上1メソッドにまとめた。
    multi_process(target, feature_index, func, sub_func)

    logger.info("apply finished.")


def multi_process(target: str, feature_index: str, func: Callable, sub_func: Callable) -> DataFrame:
    """ shots_dataインデックス読み取り """

    shots_meta_index: str = "shots-" + target + "-meta"
    shots_index: str = "shots-" + target + "-data"

    dr = DataReader()

    shots_meta_df: DataFrame = dr.read_shots_meta(shots_meta_index)
    num_of_shots: int = len(shots_meta_df)

    # データをプロセッサの数に均等分配
    shots_num_by_proc: List[int] = [(num_of_shots + i) // common.NUM_OF_PROCESS for i in range(common.NUM_OF_PROCESS)]
    logger.debug(f"shots_num_by_proc: {shots_num_by_proc}")

    procs: List[multiprocessing.context.Process] = []
    start_shot_number: int = 1
    # Nショット分をまとめてプロセスに割当。
    for shots_num in shots_num_by_proc:
        logger.debug(f"start_shot_number: {start_shot_number}")
        end_shot_number: int = start_shot_number + shots_num
        logger.debug(f"end_shot_number: {end_shot_number}")

        proc: multiprocessing.context.Process = multiprocessing.Process(
            target=apply_logic,
            args=(feature_index, shots_index, shots_meta_df, start_shot_number, end_shot_number, func, sub_func),
        )
        proc.start()
        procs.append(proc)

        start_shot_number: int = end_shot_number

    for proc in procs:
        proc.join()


def apply_logic(
    feature_index: str,
    shots_index: str,
    shots_meta_df: DataFrame,
    start_shot_number: int,
    end_shot_number: int,
    func: Callable,
    sub_func: Callable = None,
) -> List[dict]:
    """ ショットに対しロジック(func)適用 """

    result: List[dict] = []

    dr = DataReader()
    shots_df_in_proc: DataFrame = dr.read_shots(shots_index, start_shot_number, end_shot_number)

    for shot_number in range(start_shot_number, end_shot_number):
        shot_df: DataFrame = shots_df_in_proc[shots_df_in_proc.shot_number == shot_number].reset_index()
        spm: float = shots_meta_df[shots_meta_df.shot_number == shot_number].spm

        indices: List[int]
        values: List[float]
        indices, values, debug_values = ef.extract_features(shot_df, spm, func, sub_func=sub_func)

        for i in range(0, common.NUM_OF_LOAD_SENSOR):
            result.append(
                {
                    "shot_number": shot_number,
                    "load": "load0" + str(i + 1),
                    "sequential_number": shot_df.iloc[indices[i]].sequential_number,
                    "sequential_number_by_shot": indices[i],
                    "value": values[i],
                }
            )

    ElasticManager.bulk_insert(result, feature_index)


def apply_all(target: str, max_func: Callable, start_func: Callable, break_func: Callable, sub_func: Callable = None):
    """ 3,000 ショット適用処理のエントリポイント """

    logger.info("apply start.")

    shots_index: str = "shots-" + target + "-data"
    shots_meta_index: str = "shots-" + target + "-meta"

    max_point_index: str = "shots-" + target + "-max-point"
    ElasticManager.delete_exists_index(index=max_point_index)

    start_point_index: str = "shots-" + target + "-start-point"
    ElasticManager.delete_exists_index(index=start_point_index)

    break_point_index: str = "shots-" + target + "-break-point"
    ElasticManager.delete_exists_index(index=break_point_index)

    multi_process_apply_analyze_logic(
        shots_index,
        shots_meta_index,
        max_point_index,
        start_point_index,
        break_point_index,
        max_func,
        start_func,
        break_func,
        sub_func,
        common.NUM_OF_PROCESS,
    )

    logger.info("apply finished.")


def multi_process_apply_analyze_logic(
    shots_index: str,
    shots_meta_index: str,
    max_point_index: str,
    start_point_index: str,
    break_point_index: str,
    max_func: Callable,
    start_func: Callable,
    break_func: Callable,
    sub_func: Callable,
    num_of_process: int,
):
    """ ショットデータをバッチにし、マルチプロセスで分析ロジック適用 """

    dr = DataReader()

    shots_meta_df: DataFrame = dr.read_shots_meta(shots_meta_index)
    num_of_shots: int = len(shots_meta_df)

    # データをプロセッサの数に均等分配
    shots_num_by_proc: List[int] = [(num_of_shots + i) // num_of_process for i in range(num_of_process)]

    procs: List[multiprocessing.context.Process] = []
    start_shot_number: int = 1
    for shots_num in shots_num_by_proc:
        end_shot_number: int = start_shot_number + shots_num

        proc: multiprocessing.context.Process = multiprocessing.Process(
            target=apply_all_analyze_logic,
            args=(
                shots_index,
                shots_meta_df,
                start_shot_number,
                end_shot_number,
                max_point_index,
                start_point_index,
                break_point_index,
                max_func,
                start_func,
                break_func,
                sub_func,
            ),
        )
        proc.start()
        procs.append(proc)

        start_shot_number: int = end_shot_number

    for proc in procs:
        proc.join()


def apply_all_analyze_logic(
    shots_index: str,
    shots_meta_df: DataFrame,
    start_shot_number: int,
    end_shot_number: int,
    max_point_index: str,
    start_point_index: str,
    break_point_index: str,
    max_func: Callable,
    start_func: Callable,
    break_func: Callable,
    sub_func: Callable,
):
    """ ショットのDataFrameに対し、最大荷重点、荷重開始点、破断点の算出ロジックを適用し、Elasticsearchに格納する """

    dr = DataReader()

    logger.debug(f"process {os.getpid()}: data read start. shot_number: {start_shot_number} - {end_shot_number-1}.")

    # 1プロセスが処理するショットのデータを取得
    shots_df: DataFrame = dr.read_shots(shots_index, start_shot_number, end_shot_number)

    logger.info(
        f"process {os.getpid()}: data read finished. shot_number: {start_shot_number} - {end_shot_number-1}. data count: {len(shots_df)}"
    )

    max_points: List[dict] = apply_analyze_logic(shots_df, shots_meta_df, start_shot_number, end_shot_number, max_func)
    ElasticManager.bulk_insert(max_points, max_point_index)

    logger.debug(f"PID: {os.getpid()}. max point recorded.")

    start_points: List[dict] = apply_analyze_logic(
        shots_df, shots_meta_df, start_shot_number, end_shot_number, start_func
    )
    ElasticManager.bulk_insert(start_points, start_point_index)

    logger.debug(f"PID: {os.getpid()}. start point recorded.")

    break_points: List[dict] = apply_analyze_logic(
        shots_df, shots_meta_df, start_shot_number, end_shot_number, break_func, sub_func
    )
    ElasticManager.bulk_insert(break_points, break_point_index)

    logger.debug(f"PID: {os.getpid()}. break point recorded.")


def apply_analyze_logic(
    shots_df: DataFrame,
    shots_meta_df: DataFrame,
    start_shot_number: int,
    end_shot_number: int,
    func: Callable,
    sub_func: Callable = None,
) -> List[dict]:
    """ ショットに対しロジック(func)適用 """

    result: List[dict] = []

    for shot_number in range(start_shot_number, end_shot_number):
        shot_df: DataFrame = shots_df[shots_df.shot_number == shot_number].reset_index()
        spm: float = shots_meta_df[shots_meta_df.shot_number == shot_number].spm

        indices: List[int]
        values: List[float]
        indices, values, debug_values = ef.extract_features(shot_df, spm, func, sub_func=sub_func)

        for i in range(0, common.NUM_OF_LOAD_SENSOR):
            result.append(
                {
                    "shot_number": shot_number,
                    "load": "load0" + str(i + 1),
                    "sequential_number": shot_df.iloc[indices[i]].sequential_number,
                    "sequential_number_by_shot": indices[i],
                    "value": values[i],
                }
            )

    return result


def simple_apply(
    target: str, shots_df: DataFrame, shots_meta_df: DataFrame, feature: str, func: Callable, sub_func: Callable = None
):
    """ シングルプロセスで全ショットににロジック適用。データ呼び出し側で用意する。 """

    result: List[dict] = []

    for shot_number in range(1, len(shots_meta_df) + 1):
        shot_df = shots_df[shots_df.shot_number == shot_number].reset_index()
        spm = shots_meta_df[shots_meta_df.shot_number == shot_number].spm

        indices: List[int]
        values: List[float]
        indices, values, debug_values = ef.extract_features(shot_df, spm, func, sub_func=sub_func)

        for i in range(0, common.NUM_OF_LOAD_SENSOR):
            result.append(
                {
                    "shot_number": shot_number,
                    "load": "load0" + str(i + 1),
                    "sequential_number": shot_df.iloc[indices[i]].sequential_number,
                    "sequential_number_by_shot": indices[i],
                    "value": values[i],
                }
            )

    feature_index: str = "shots-" + target + "-" + feature + "-point"
    ElasticManager.delete_exists_index(index=feature_index)
    ElasticManager.bulk_insert(result, feature_index)


def extract_break_channels(values: List[float]) -> Tuple[str, str]:
    """ 4ch分の破断点の荷重値リストを受け取り、破断側のチャネルセットを返す。 """

    min_index = values.index(min(values))

    # 最小値のindex = 0 or 1 のとき、ch01, ch02が破断側
    if min_index in (0, 1):
        return ("load01", "load02")
    # 最小値のindex = 2 or 3 のとき、ch03, ch04が破断側
    else:
        return ("load03", "load04")


if __name__ == "__main__":
    LOG_FILE: Final[str] = os.path.join(
        common.get_config_value(common.APP_CONFIG_PATH, "log_dir"), "analyze/analyze.log"
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

    # apply(target="20201201010000", feature="max", func=ef.max_load, sub_func=ef.narrowing_var_ch)
    # apply(target="20201201010000", feature="start", func=ef.load_start2)
    # apply(target="20201201010000", feature="break", func=ef.breaking_var_vrms, sub_func=ef.narrowing_var_ch)

    # apply_all(
    #     target="20201201010000",
    #     max_func=ef.max_load,
    #     start_func=ef.load_start2,
    #     break_func=ef.breaking_varmax29
    #     # break_func=ef.breaking_var_vrms,
    #     # sub_func=ef.narrowing_var_ch,
    # )

    # target = "20201201010000"
    # shots_data_index = "shots-" + target + "-data"

    # dr = DataReader()
    # shots_df = dr.read_all(shots_data_index)

    # shots_meta_index = "shots-" + target + "-meta"
    # shots_meta_df = dr.read_shots_meta(shots_meta_index)

    # simple_apply(
    #     target=target, shots_df=shots_df, shots_meta_df=shots_meta_df, feature="max", func=ef.max_load, sub_func=None,
    # )
