from typing import List
from datetime import datetime, timedelta
from backend.app.models.data_collect_history import DataCollectHistory
from backend.app.schemas.data_collect_history import DataCollectHistoryUpdate
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
                joinedload(DataCollectHistory.machine), joinedload(DataCollectHistory.data_collect_history_details)
            )
            .all()
        )

        return history

    @staticmethod
    def select_by_id(db: Session, id: int) -> DataCollectHistory:
        history: DataCollectHistory = db.query(DataCollectHistory).get(id)

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

    @staticmethod
    def select_by_machine_id_started_at(db: Session, machine_id: str, target_datetime_str: str) -> DataCollectHistory:

        started_at: datetime = datetime.strptime(target_datetime_str, "%Y%m%d%H%M%S") - timedelta(hours=9)
        history: DataCollectHistory = (
            db.query(DataCollectHistory)
            .filter(DataCollectHistory.machine_id == machine_id)
            .filter(DataCollectHistory.started_at == started_at)
            .one()
        )

        return history

    @staticmethod
    def update(db: Session, db_obj: DataCollectHistory, obj_in: DataCollectHistoryUpdate) -> DataCollectHistory:

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        # 更新対象のプロパティをセット
        for key, value in update_data.items():
            # NOTE: プロパティにList[DataCollectHistoryDetail]を直接代入するとエラーになるため、ループしてセット
            if key == "data_collect_history_details":
                for detail_number, detail in enumerate(value):
                    for k, v in detail.items():
                        setattr(db_obj.data_collect_history_details[detail_number], k, v)
            else:
                setattr(db_obj, key, value)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, db_obj: DataCollectHistory) -> DataCollectHistory:
        db.delete(db_obj)
        db.commit()
        return db_obj
