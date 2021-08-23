from typing import List
from backend.data_collect_manager.models.data_collect_history import DataCollectHistory
from sqlalchemy.orm import joinedload
from sqlalchemy import desc


class DataCollectHistoryDAO:
    @staticmethod
    def select_all() -> List[DataCollectHistory]:
        history: List[DataCollectHistory] = (
            DataCollectHistory.query.order_by(desc(DataCollectHistory.started_at))
            .options(
                joinedload(DataCollectHistory.machine),
            )
            .all()
        )

        return history
