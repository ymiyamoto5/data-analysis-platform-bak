from typing import List
from backend.app.models.data_collect_history_detail import DataCollectHistoryDetail
from sqlalchemy.orm import joinedload
from sqlalchemy import desc
from sqlalchemy.orm import Session


class CRUDDataCollectHistoryDetail:
    @staticmethod
    def update(db: Session, history_details: List[DataCollectHistoryDetail]):
        pass
