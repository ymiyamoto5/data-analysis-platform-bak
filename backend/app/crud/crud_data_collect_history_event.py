from backend.app.models.data_collect_history_events import DataCollectHistoryEvent
from sqlalchemy import desc
from sqlalchemy.orm import Session


class CRUDDataCollectHistoryEvent:
    @staticmethod
    def select_latest_by_history_id(db: Session, data_collect_history_id: str) -> DataCollectHistoryEvent:
        event: DataCollectHistoryEvent = (
            db.query(DataCollectHistoryEvent)
            .filter_by(data_collect_history_id=data_collect_history_id)
            .order_by(desc(DataCollectHistoryEvent.occurred_at))
            .first()
        )

        return event

    @staticmethod
    def count_by_history_id(db: Session, data_collect_history_id: str) -> int:
        count: int = (
            db.query(DataCollectHistoryEvent).filter_by(data_collect_history_id=data_collect_history_id).count()
        )

        return count
