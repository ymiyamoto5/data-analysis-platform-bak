from typing import List
from backend.app.models.data_collect_history import DataCollectHistory
from sqlalchemy.orm import joinedload
from sqlalchemy import desc
from sqlalchemy.orm import Session


class CRUDDataCollectHistory:
    @staticmethod
    def select_all(db: Session) -> List[DataCollectHistory]:
        history: List[DataCollectHistory] = (
            db.query(DataCollectHistory)
            .order_by(desc(DataCollectHistory.started_at))
            .options(
                joinedload(DataCollectHistory.machine),
            )
            .all()
        )

        return history

    @staticmethod
    def select_by_machine_id(db: Session, machine_id: str) -> List[DataCollectHistory]:
        history: List[DataCollectHistory] = (
            db.query(DataCollectHistory)
            .filter_by(machine_id=machine_id)
            .order_by(desc(DataCollectHistory.started_at))
            .options(
                joinedload(DataCollectHistory.machine),
            )
            .all()
        )

        return history
