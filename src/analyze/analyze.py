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

    dr = DataReader()

    shots_index: str = "shots-" + target + "-data"

    shots_meta_index: str = "shots-" + target + "-meta"

    # TODO: 並列化

    shots_df: DataFrame = dr.read_shots(shots_index, 1, 6)

    shots_meta_df: DataFrame = dr.read_shots_meta(shots_meta_index)

    shots_meta_df = shots_meta_df[0:5]

    max_points: List[dict] = apply_analyze_logic_to_all_shots(shots_df, shots_meta_df, ef.max_load)
    start_points: List[dict] = apply_analyze_logic_to_all_shots(shots_df, shots_meta_df, ef.load_start2)
    break_points: List[dict] = apply_analyze_logic_to_all_shots(
        shots_df, shots_meta_df, ef.breaking_varmax29idiff_tmpfix
    )

    max_point_index: str = "shots-features-" + target + "-max-point"
    ElasticManager.delete_exists_index(index=max_point_index)

    start_point_index: str = "shots-features-" + target + "-start-point"
    ElasticManager.delete_exists_index(index=start_point_index)

    break_point_index: str = "shots-features-" + target + "-break-point"
    ElasticManager.delete_exists_index(index=break_point_index)

    ElasticManager.bulk_insert(max_points, max_point_index, 5000)
    ElasticManager.bulk_insert(start_points, start_point_index, 5000)
    ElasticManager.bulk_insert(break_points, break_point_index, 5000)


def apply_analyze_logic_to_all_shots(shots_df, shots_meta_df, func) -> List[dict]:
    """ """

    result: List[dict] = []

    for shot_number in range(1, len(shots_meta_df) + 1):
        shot_df: DataFrame = shots_df[shots_df.shot_number == shot_number]
        shot_df = shot_df.reset_index()
        spm: float = shots_meta_df[shots_meta_df.shot_number == shot_number].spm

        indices: List[int]
        values: List[float]
        indices, values = ef.extract_features(shot_df, spm, func)

        for i in range(0, 4):
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

