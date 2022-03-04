import os
from datetime import datetime, timedelta
from typing import List

from backend.app.models.data_collect_history import DataCollectHistory
from backend.app.models.data_collect_history_gateway import DataCollectHistoryGateway
from backend.app.models.data_collect_history_handler import DataCollectHistoryHandler
from backend.app.models.data_collect_history_sensor import DataCollectHistorySensor
from backend.app.schemas.data_collect_history import DataCollectHistoryUpdate
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload


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
        # NOTE: ミリ秒以下の情報が抜け落ちているため完全一致ではfilterできない。1秒範囲内で一致確認する。
        history: DataCollectHistory = (
            db.query(DataCollectHistory)
            .filter(DataCollectHistory.machine_id == machine_id)
            .filter(
                DataCollectHistory.started_at >= started_at,
                DataCollectHistory.started_at <= started_at + timedelta(seconds=1),
            )
            .one()
        )

        return history

    @staticmethod
    def select_by_machine_id_target_dir(db: Session, machine_id: str, target_dir: str) -> DataCollectHistory:
        """退避ディレクトリパスに含まれる日時から特定した履歴を取得する"""

        processed_dir_path: str = os.path.join(os.environ["data_dir"], f"{machine_id}-{target_dir}")

        history: DataCollectHistory = (
            db.query(DataCollectHistory).filter_by(machine_id=machine_id).filter_by(processed_dir_path=processed_dir_path).one()
        )

        return history

    @staticmethod
    def select_latest_by_machine_id(db: Session, machine_id: str) -> DataCollectHistory:
        history: DataCollectHistory = (
            db.query(DataCollectHistory)
            .filter_by(machine_id=machine_id)
            .order_by(desc(DataCollectHistory.started_at))
            .options(
                joinedload(DataCollectHistory.machine),
            )
            .first()
        )

        return history

    @staticmethod
    def select_latest_by_machine_gateway_handler_id(
        db: Session, machine_id: str, gateway_id: str, handler_id: str
    ) -> DataCollectHistoryHandler:
        history: DataCollectHistoryHandler = (
            db.query(DataCollectHistoryHandler)
            .filter(DataCollectHistoryHandler.handler_id == handler_id)
            .join(DataCollectHistoryGateway)
            .filter(DataCollectHistoryGateway.gateway_id == gateway_id)
            .join(DataCollectHistory)
            .filter(DataCollectHistory.machine_id == machine_id)
            .order_by(desc(DataCollectHistory.started_at))
            .first()
        )

        # joinする場合の例
        # db.query(DataCollectHistory,DataCollectHistoryGateway,DataCollectHistoryHandler).filter(DataCollectHistory.machine_id==machine_id)
        # .join(DataCollectHistory.data_collect_history_gateways).filter(DataCollectHistoryGateway.gateway_id==gateway_id)
        # .join(DataCollectHistoryGateway.data_collect_history_handlers).filter(DataCollectHistoryHandler.handler_id==handler_id).all()

        return history

    @staticmethod
    def update(db: Session, db_obj: DataCollectHistory, obj_in: DataCollectHistoryUpdate) -> DataCollectHistory:

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        # 更新対象のプロパティをセット
        for key, value in update_data.items():
            # NOTE: プロパティにList[DataCollectHistorySensor]を直接代入するとエラーになるため、ループしてセット
            if key == "data_collect_history_sensors":
                for detail_number, detail in enumerate(value):
                    for k, v in detail.items():
                        setattr(db_obj.data_collect_history_sensors[detail_number], k, v)
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
