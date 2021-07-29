import os
import sys
import pandas as pd
import inspect
from typing import List
from pandas.core.frame import DataFrame

from logger.logger import init_logger, get_logger

# module_name: str = os.path.splitext(os.path.basename(__file__))[0]
# init_logger(module_name)
# logger = get_logger(module_name)

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from elastic_manager.elastic_manager import ElasticManager

sys.path.append(os.path.join(os.path.dirname(__file__), "../utils"))
import common  # noqa


class EventManager:
    @staticmethod
    def fetch_events(events_index: str) -> List[dict]:
        query: dict = {"sort": {"event_id": {"order": "asc"}}}
        events: List[dict] = ElasticManager.get_docs(index=events_index, query=query)

        return events

