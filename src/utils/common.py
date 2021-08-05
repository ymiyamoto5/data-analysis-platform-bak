"""
 ==================================
  common.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import os
import json
import logging
import multiprocessing

from typing import Final, List
from datetime import datetime, timedelta
from pytz import timezone
from enum import Enum

logger = logging.getLogger(__name__)

# グローバル定数
APP_CONFIG_PATH: Final[str] = os.getenv("APP_CONFIG_PATH", "/home/hone/h-one-experimental-system/app_config.json")
MAX_LOG_SIZE: Final[int] = 1024 * 1024  # 1MB
BACKUP_COUNT: Final[int] = 5
ELASTIC_MAX_DOC_SIZE: Final[int] = 10_000
MARGIN: Final[float] = 0.1
SAMPLING_RATE: Final[int] = 100_000
SAMPLING_INTERVAL: Final[float] = 0.000010
TIMESTAMP_MAX: Final[float] = datetime.max.replace(tzinfo=timezone("UTC")).timestamp()
NUM_OF_PROCESS: Final[int] = multiprocessing.cpu_count()
NUM_OF_LOAD_SENSOR: Final[int] = 4
LOG_LEVEL: List[str] = ["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"]
DEFAULT_LOG_LEVEL: Final[str] = "INFO"
USER_CHOICE: List[str] = LOG_LEVEL + list(map(lambda w: w.lower(), LOG_LEVEL))


class STATUS(Enum):
    STOP = "stop"
    RUNNING = "running"


def get_config_value(file_path: str, key: str):
    """ 対象ファイルのkeyを読み、valueを返す """

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
    """ 表示用時刻(JST) """

    def __init__(self, value: datetime):
        # self.__value: datetime = value.astimezone(timezone("Asia/Tokyo"))
        self.__value: datetime = value + timedelta(hours=+9)

    @property
    def value(self) -> datetime:
        return self.__value

    def to_string(self) -> str:
        return datetime.strftime(self.__value, "%Y%m%d%H%M%S")
