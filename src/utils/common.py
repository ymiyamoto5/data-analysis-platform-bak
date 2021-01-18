import os
import sys
import json
import logging

from typing import Final, List, Optional
from datetime import datetime
from pytz import timezone

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from elastic_manager.elastic_manager import ElasticManager


logger = logging.getLogger(__name__)

# グローバル変数
APP_CONFIG_PATH: Final[str] = "/home/ymiyamoto5/h-one-experimental-system/app_config.json"
MARGIN: Final[int] = 0.1
SAMPLING_RATE: Final[int] = 100_000
SAMPLING_INTERVAL: Final[int] = 0.000010


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


def get_events(suffix: str) -> List[dict]:
    """ 対応するevents_indexのデータ取得 """

    events_index: str = "events-" + suffix
    query: dict = {"sort": {"event_id": {"order": "asc"}}}
    events: List[dict] = ElasticManager.get_all_doc(events_index, query)

    return events


class DisplayTime:
    """ 表示用時刻(JST) """

    def __init__(self, value: datetime):
        self.__value: datetime = value.astimezone(timezone("Asia/Tokyo"))

    @property
    def value(self) -> datetime:
        return self.__value

    def to_string(self) -> str:
        return datetime.strftime(self.__value, "%Y%m%d%H%M%S")
