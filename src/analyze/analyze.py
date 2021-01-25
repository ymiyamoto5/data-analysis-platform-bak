import warnings

warnings.simplefilter("ignore")
import multiprocessing
import os
import sys
import logging
import logging.handlers
import pandas as pd
from typing import Callable, Final, List, Optional
from pandas.core.frame import DataFrame

import h_one_extract_features as ef

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from elastic_manager.elastic_manager import ElasticManager
from data_reader.data_reader import DataReader

sys.path.append(os.path.join(os.path.dirname(__file__), "../utils"))
from time_logger import time_log
from throughput_counter import throughput_counter
import common

LOG_FILE: Final[str] = os.path.join(common.get_config_value(common.APP_CONFIG_PATH, "log_dir"), "analyze/analyze.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=common.MAX_LOG_SIZE, backupCount=common.BACKUP_COUNT),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@time_log
def main(target: str):
    """ """

    shots_index: str = "shots-" + target + "-data"
    shots_meta_index: str = "shots-" + target + "-meta"

    max_point_index: str = "shots-" + target + "-max-point"
    ElasticManager.delete_exists_index(index=max_point_index)

    start_point_index: str = "shots-" + target + "-start-point"
    ElasticManager.delete_exists_index(index=start_point_index)

    break_point_index: str = "shots-" + target + "-break-point"
    ElasticManager.delete_exists_index(index=break_point_index)

    multi_process_apply_analyze_logic(
        shots_index, shots_meta_index, max_point_index, start_point_index, break_point_index, common.NUM_OF_PROCESS
    )


def multi_process_apply_analyze_logic(
    shots_index: str,
    shots_meta_index: str,
    max_point_index: str,
    start_point_index: str,
    break_point_index: str,
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
):
    """ ショットのDataFrameに対し、最大荷重点、荷重開始点、破断点の算出ロジックを適用し、Elasticsearchに格納する """

    dr = DataReader()

    # 1プロセスが処理するショットのデータを取得
    shots_df: DataFrame = dr.read_shots(shots_index, start_shot_number, end_shot_number)

    logger.info(
        f"process {os.getpid()} will execute shot_number: {start_shot_number} - {end_shot_number-1}. data count: {len(shots_df)}"
    )

    max_points: List[dict] = apply_analyze_logic(
        shots_df, shots_meta_df, start_shot_number, end_shot_number, ef.max_load
    )
    ElasticManager.bulk_insert(max_points, max_point_index)

    logger.info(f"PID: {os.getpid()}. max point recorded.")

    start_points: List[dict] = apply_analyze_logic(
        shots_df, shots_meta_df, start_shot_number, end_shot_number, ef.load_start2
    )
    ElasticManager.bulk_insert(start_points, start_point_index)

    logger.info(f"PID: {os.getpid()}. start point recorded.")

    break_points: List[dict] = apply_analyze_logic(
        shots_df, shots_meta_df, start_shot_number, end_shot_number, ef.breaking_varmax29
    )
    ElasticManager.bulk_insert(break_points, break_point_index)

    logger.info(f"PID: {os.getpid()}. break point recorded.")


def apply_analyze_logic(
    shots_df: DataFrame, shots_meta_df: DataFrame, start_shot_number: int, end_shot_number: int, func: Callable
) -> List[dict]:
    """ ショットに対しロジック(func)適用 """

    result: List[dict] = []

    for shot_number in range(start_shot_number, end_shot_number):
        shot_df: DataFrame = shots_df[shots_df.shot_number == shot_number]
        spm: float = shots_meta_df[shots_meta_df.shot_number == shot_number].spm

        indices: List[int]
        values: List[float]
        indices, values = ef.extract_features(shot_df, spm, func)

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


if __name__ == "__main__":

    main(target="20201201010000")

