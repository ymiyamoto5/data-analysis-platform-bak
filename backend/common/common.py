"""
 ==================================
  common.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import json
import multiprocessing
import sys
from datetime import datetime, timedelta
from enum import Enum
from typing import Final, List, Optional, Tuple, Union

from backend.app.models.data_collect_history_handler import DataCollectHistoryHandler
from backend.app.models.data_collect_history_sensor import DataCollectHistorySensor
from backend.app.models.sensor import Sensor
from backend.common.common_logger import logger
from pytz import timezone

# グローバル定数
ELASTIC_MAX_DOC_SIZE: Final[int] = 10_000
TIMESTAMP_MAX: Final[float] = datetime.max.replace(tzinfo=timezone("UTC")).timestamp()
NUM_OF_PROCESS: Final[int] = multiprocessing.cpu_count()
NUM_OF_LOAD_SENSOR: Final[int] = 4
ID_PATTERN: Final[str] = "^[0-9a-zA-Z-]+$"
CUT_OUT_SHOT_SENSOR_TYPES: Final[Tuple[str, ...]] = ("stroke_displacement", "pulse")
INT_MAX: Final[int] = 2_147_483_647
CSV_PATTERN: Final[str] = r"\.csv$"
DATETIME_STR_LENGTH = 14


class Severity(str, Enum):
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class STATUS(Enum):
    STOP = "stop"
    RUNNING = "running"


class COLLECT_STATUS(Enum):
    SETUP = "setup"
    START = "start"
    PAUSE = "pause"
    RESUME = "resume"
    STOP = "stop"
    RECORDED = "recorded"


def get_config_value(file_path: str, key: str):
    """対象ファイルのkeyを読み、valueを返す"""

    try:
        with open(file_path, "r") as f:
            config: dict = json.load(f)
    except Exception as e:
        logger.exception(str(e))
        raise e

    value = config.get(key)

    if value is None:
        logger.error(f"Key {key} is not found in {file_path}")
        raise KeyError

    return value


class DisplayTime:
    """表示用時刻(JST)"""

    def __init__(self, value: datetime):
        self.__value: datetime = value + timedelta(hours=+9)

    @property
    def value(self) -> datetime:
        return self.__value

    def to_string(self) -> str:
        return datetime.strftime(self.__value, "%Y%m%d%H%M%S")


def increment_sequence_number(sequence_number: int) -> int:
    """sequence_numberがC言語のint最大値を超えた場合は1に初期化、それ以外はインクリメントする。"""

    return 1 if sequence_number >= INT_MAX else sequence_number + 1


def get_cut_out_shot_sensor(
    sensors: Union[List[Sensor], List[DataCollectHistorySensor]]
) -> Optional[Union[Sensor, DataCollectHistorySensor]]:
    """ショット切り出し対象となるセンサーを特定する"""
    cut_out_sensor: Union[List[Sensor], List[DataCollectHistorySensor]] = [
        s for s in sensors if s.sensor_type_id in CUT_OUT_SHOT_SENSOR_TYPES
    ]

    # 変位センサーは機器にただひとつのみ紐づいている前提
    if len(cut_out_sensor) > 1:
        logger.error(f"Only one displacement sensor is needed. num_of_displacement_sensor: {cut_out_sensor}")
        sys.exit(1)

    return None if len(cut_out_sensor) == 0 else cut_out_sensor[0]


def get_main_handler(handlers: List[DataCollectHistoryHandler]) -> DataCollectHistoryHandler:
    """代表ハンドラーを選択する"""

    if len(handlers) == 1:
        handler: DataCollectHistoryHandler = handlers[0]
    else:
        handler = [x for x in handlers if x.is_primary][0]

    return handler
