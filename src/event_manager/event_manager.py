import os
import sys
import pandas as pd
from datetime import datetime
from typing import List, Optional
from pandas.core.frame import DataFrame

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from elastic_manager.elastic_manager import ElasticManager

sys.path.append(os.path.join(os.path.dirname(__file__), "../utils"))
import common  # noqa


class EventManager:
    @staticmethod
    def fetch_events(events_index: str) -> List[dict]:
        """ events_index からイベント情報を取得し、返却する """

        logger.info(f"Fetch events from {events_index}.")

        query: dict = {"sort": {"event_id": {"order": "asc"}}}
        events: List[dict] = ElasticManager.get_docs(index=events_index, query=query)

        return events

    @staticmethod
    def get_collect_start_time(events: List[dict]) -> Optional[float]:
        """ イベントリストから収集開始時間を取得し、timestampにして返却する """

        start_events: List[dict] = [x for x in events if x["event_type"] == "start"]

        if len(start_events) == 0:
            logger.error("Data collection has not started yet.")
            sys.exit(1)

        start_event: dict = start_events[0]
        collect_start_time: float = datetime.fromisoformat(start_event["occurred_time"]).timestamp()

        return collect_start_time

    @staticmethod
    def get_pause_events(events: List[dict]) -> List[dict]:
        """ events_indexから中断イベントを取得し、timestampにして返却する。 """

        pause_events: List[dict] = [x for x in events if x["event_type"] == "pause"]
        if len(pause_events) > 0:
            for pause_event in pause_events:
                if pause_event.get("start_time") is None:
                    logger.exception("Invalid status in pause event. Not found [start_time] key.")
                    raise KeyError

                if pause_event.get("end_time") is None:
                    logger.exception("Pause event does not finished. Please retry after finish pause.")
                    raise KeyError
                # str to datetime
                pause_event["start_time"] = datetime.fromisoformat(pause_event["start_time"])
                pause_event["end_time"] = datetime.fromisoformat(pause_event["end_time"])
                # datetime to unixtime
                pause_event["start_time"] = pause_event["start_time"].timestamp()
                pause_event["end_time"] = pause_event["end_time"].timestamp()

        return pause_events

