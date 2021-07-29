import os
import sys
from datetime import datetime, timedelta
from typing import List, Optional, Final

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
    def get_collect_setup_time(events: List[dict]) -> Optional[float]:
        """ events_indexから収集（段取）開始時間を取得 """

        setup_events: List[dict] = [x for x in events if x["event_type"] == "setup"]

        if len(setup_events) == 0:
            logger.error("Data collection has not setup yet.")
            raise sys.exit(1)

        setup_event: dict = setup_events[0]
        collect_start_time: float = datetime.fromisoformat(setup_event["occurred_time"]).timestamp()

        return collect_start_time

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
    def get_collect_end_time(events: List[dict]) -> float:
        """ events_indexから収集終了時間を取得 """

        end_events: List[dict] = [x for x in events if x["event_type"] == "stop"]

        if len(end_events) == 0:
            logger.info("Data collect is not finished yet. end_time is set to max.")
            end_time: float = common.TIMESTAMP_MAX
        else:
            end_event: dict = end_events[0]
            BUFFER: Final[float] = 5.0  # 安全バッファ
            end_time = datetime.fromisoformat(end_event["occurred_time"]).timestamp() + BUFFER

        return end_time

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

    @staticmethod
    def get_tag_events(events: List[dict], back_seconds_for_tagging: int = 120) -> List[dict]:
        """ events_indexからタグ付け区間を取得。
            記録された時刻（end_time）からN秒前(back_seconds_for_tagging)に遡り、start_timeとする。
        """

        tag_events: List[dict] = [x for x in events if x["event_type"] == "tag"]
        logger.info(tag_events)

        if len(tag_events) > 0:
            for tag_event in tag_events:
                if tag_event.get("end_time") is None:
                    logger.exception("Invalid status in tag event. Not found [end_time] key.")
                    raise KeyError

                tag_event["end_time"] = datetime.fromisoformat(tag_event["end_time"])
                tag_event["start_time"] = tag_event["end_time"] - timedelta(seconds=back_seconds_for_tagging)
                # DataFrameのtimestampと比較するため、datetimeからtimestampに変換
                tag_event["start_time"] = tag_event["start_time"].timestamp()
                tag_event["end_time"] = tag_event["end_time"].timestamp()

        return tag_events
