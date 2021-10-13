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
import os
from datetime import datetime, timedelta
from enum import Enum
from typing import Final

from backend.common.common_logger import logger
from pytz import timezone

# グローバル定数
APP_CONFIG_PATH: Final[str] = os.getenv("APP_CONFIG_PATH", "default_config_path.json")
ELASTIC_MAX_DOC_SIZE: Final[int] = 10_000
TIMESTAMP_MAX: Final[float] = datetime.max.replace(tzinfo=timezone("UTC")).timestamp()
NUM_OF_PROCESS: Final[int] = multiprocessing.cpu_count()
NUM_OF_LOAD_SENSOR: Final[int] = 4
ID_PATTERN: Final[str] = "^[0-9a-zA-Z-]+$"


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
