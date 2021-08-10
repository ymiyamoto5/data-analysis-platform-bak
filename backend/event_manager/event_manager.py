import sys
from datetime import datetime, timedelta
from typing import List, Optional, Final, Tuple
from backend.common.common_logger import logger
from backend.elastic_manager.elastic_manager import ElasticManager
from backend.common import common  # noqa


class EventManager:
    @staticmethod
    def create_events_index(datetime_str: str) -> Tuple[bool, str]:
        """日時文字列をsuffixとするevents_indexを作成する"""

        events_index: str = "events-" + datetime_str
        successful: bool = ElasticManager.create_index(events_index)

        return successful, events_index

    @staticmethod
    def record_event(events_index: str, event_type: str, occurred_time: datetime) -> bool:
        """イベントをevents_indexに保存する"""

        doc_id: int = ElasticManager.count(events_index)
        query = {"event_id": doc_id, "event_type": event_type, "occurred_time": occurred_time}
        successful: bool = ElasticManager.create_doc(events_index, doc_id, query)

        return successful

    @staticmethod
    def record_tag_event(events_index: str, tag: str, occurred_time: datetime) -> bool:
        """タグイベントをevents_indexに保存する"""

        doc_id: int = ElasticManager.count(events_index)
        query: dict = {"event_id": doc_id, "event_type": "tag", "tag": tag, "end_time": occurred_time}
        successful: bool = ElasticManager.create_doc(events_index, doc_id, query)

        return successful

    @staticmethod
    def update_pause_event(events_index: str, occurred_time: datetime) -> bool:
        """中断イベントを更新する"""

        # 更新対象は最新のdocument（pause）イベントである前提
        latest_event_type: str = EventManager.get_latest_event(events_index)[0]["event_type"]
        # TODO: エラーハンドリング
        if latest_event_type != "pause":
            logger.error(f"latest event type is invalid status {latest_event_type}")

        doc_id: int = ElasticManager.count(events_index) - 1
        query: dict = {"end_time": occurred_time}
        successful: bool = ElasticManager.update_doc(events_index, doc_id, query)

        return successful

    @staticmethod
    def get_latest_events_index() -> Optional[str]:
        """最新のevents_indexの名前を返す"""

        return ElasticManager.get_latest_index("events-*")

    @staticmethod
    def get_latest_event(events_index: str) -> List[dict]:
        """最新イベントを返す"""

        query: dict = {"sort": {"event_id": {"order": "desc"}}}
        return ElasticManager.get_docs(index=events_index, query=query, size=1)

    @staticmethod
    def fetch_events(events_index: str) -> List[dict]:
        """events_index からイベント情報を取得し、返却する"""

        logger.info(f"Fetch events from {events_index}.")

        query: dict = {"sort": {"event_id": {"order": "asc"}}}
        events: List[dict] = ElasticManager.get_docs(index=events_index, query=query)

        return events

    @staticmethod
    def get_collect_setup_time(events: List[dict]) -> Optional[float]:
        """events_indexから収集（段取）開始時間を取得"""

        setup_events: List[dict] = [x for x in events if x["event_type"] == "setup"]

        if len(setup_events) == 0:
            logger.error("Data collection has not setup yet.")
            sys.exit(1)

        setup_event: dict = setup_events[0]
        collect_start_time: float = datetime.fromisoformat(setup_event["occurred_time"]).timestamp()

        return collect_start_time

    @staticmethod
    def get_collect_start_time(events: List[dict]) -> Optional[float]:
        """イベントリストから収集開始時間を取得し、timestampにして返却する"""

        start_events: List[dict] = [x for x in events if x["event_type"] == "start"]

        if len(start_events) == 0:
            logger.error("Data collection has not started yet.")
            sys.exit(1)

        start_event: dict = start_events[0]
        collect_start_time: float = datetime.fromisoformat(start_event["occurred_time"]).timestamp()

        return collect_start_time

    @staticmethod
    def get_collect_end_time(events: List[dict]) -> float:
        """events_indexから収集終了時間を取得"""

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
        """events_indexから中断イベントを取得し、timestampにして返却する。"""

        pause_events: List[dict] = [x for x in events if x["event_type"] == "pause"]

        if len(pause_events) == 0:
            return []

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
        """events_indexからタグ付け区間を取得。
        記録された時刻（end_time）からN秒前(back_seconds_for_tagging)に遡り、start_timeとする。
        """

        tag_events: List[dict] = [x for x in events if x["event_type"] == "tag"]
        logger.debug(tag_events)

        if len(tag_events) == 0:
            return []

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
