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

    # @staticmethod
    # def insert(machine: Machine, started_at: datetime) -> None:
    #     """履歴の追加"""
    #     new_data_collect_history = DataCollectHistory(
    #         machine_id=machine.machine_id, machine_name=machine.machine_name, started_at=started_at, ended_at=None
    #     )  # type: ignore

    #     db.session.add(new_data_collect_history)
    #     db.session.commit()
