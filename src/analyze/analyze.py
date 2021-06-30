"""
 ==================================
  analyze.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import warnings

warnings.simplefilter("ignore")
import multiprocessing
import os
import sys
import traceback
import logging
import logging.handlers
from typing import Callable, Final, List, Tuple, Optional
from pandas.core.frame import DataFrame

import h_one_extract_features as ef

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from elastic_manager.elastic_manager import ElasticManager
from data_reader.data_reader import DataReader

sys.path.append(os.path.join(os.path.dirname(__file__), "../utils"))
import common

logger = logging.getLogger(__name__)


def apply(
    target: str,
    shots_df: DataFrame,
    shots_meta_df: DataFrame,
    feature: str,
    func: Callable,
    sub_func: Callable = None,
    exclude_shots: Tuple[int, ...] = None,
) -> None:
    """ 特定のロジックを3,000ショットに適用 """

    logger.info("apply start.")

    if feature not in ("max", "start", "break"):
        logger.error(f"feature: {feature} is invalid.")
        sys.exit(1)

    feature_index: str = "shots-" + target + "-" + feature + "-point"
    ElasticManager.delete_exists_index(index=feature_index)

    # NOTE: データ分割をNショット毎に分割/ロジック適用/ELS保存。並列処理の関係上1メソッドにまとめた。
    multi_process(shots_df, shots_meta_df, feature_index, feature, func, sub_func, exclude_shots)

    logger.info("apply finished.")


def multi_process(
    shots_df: DataFrame,
    shots_meta_df: DataFrame,
    feature_index: str,
    feature: str,
    func: Callable,
    sub_func: Callable = None,
    exclude_shots: Tuple[int, ...] = None,
) -> None:
    """ データを複数ショット単位で読み込み、ロジック適用、ELS格納 """

    # NOTE: ショットを削除した場合、ショット番号に歯抜けになるため、countではなく最終ショット番号を採用
    num_of_shots: int = shots_meta_df.shot_number.iloc[-1]

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
            args=(
                feature_index,
                shots_df,
                shots_meta_df,
                start_shot_number,
                end_shot_number,
                feature,
                func,
                sub_func,
                exclude_shots,
            ),
        )
        proc.start()
        procs.append(proc)

        start_shot_number = end_shot_number

    for proc in procs:
        proc.join()


def apply_logic(
    feature_index: str,
    shots_df: DataFrame,
    shots_meta_df: DataFrame,
    start_shot_number: int,
    end_shot_number: int,
    feature: str,
    func: Callable,
    sub_func: Callable = None,
    exclude_shots: Tuple[int] = None,
) -> None:
    """ ショットに対しロジック(func)適用 """

    result: List[dict] = []

    for shot_number in range(start_shot_number, end_shot_number):
        # 除外ショットはスキップ
        if exclude_shots is not None:
            if shot_number in exclude_shots:
                logger.info(f"shot_number: {shot_number} was excluded.")
                continue

        # 特定ショット番号のデータを抽出
        shot_df: DataFrame = shots_df[shots_df.shot_number == shot_number]

        if len(shot_df) == 0:
            logger.info(f"shot_number: {shot_number} was not found.")
            continue

        shot_df = shot_df.reset_index()

        spm: Optional[float] = shots_meta_df[shots_meta_df.shot_number == shot_number].spm
        # TODO: 後続エラー回避のため、暫定対処としてNoneのときは80.0としている
        spm = float(spm) if spm.iloc[0] is not None else 80.0

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
            break_channels: Tuple[str, str] = extract_break_channels(values)

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

    target = "20210327141514"
    shots_data_index = "shots-" + target + "-data"
    shots_meta_index = "shots-" + target + "-meta"

    dr = DataReader()
    shots_df: DataFrame = dr.multi_process_read_all(shots_data_index)
    shots_meta_df = dr.read_shots_meta(shots_meta_index)

    exclude_shots: Tuple[int, ...] = (983, 1227, 1228, 1229, 1369, 1381)

    apply(
        target=target,
        shots_df=shots_df,
        shots_meta_df=shots_meta_df,
        feature="max",
        func=ef.max_load,
        sub_func=None,
        exclude_shots=exclude_shots,
    )
    apply(
        target=target,
        shots_df=shots_df,
        shots_meta_df=shots_meta_df,
        feature="start",
        func=ef.load_start3,
        sub_func=None,
        exclude_shots=exclude_shots,
    )
    apply(
        target=target,
        shots_df=shots_df,
        shots_meta_df=shots_meta_df,
        feature="break",
        func=ef.breaking_vmin_amin,
        sub_func=ef.narrowing_v4min_mab,
        exclude_shots=exclude_shots,
    )
