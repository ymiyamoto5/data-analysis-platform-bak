from datetime import datetime
from sqlalchemy import desc
from backend.app.models.machine import Machine
from backend.app.models.data_collect_history import DataCollectHistory
from backend.common import common
from sqlalchemy.orm import Session


class CRUDController:
    @staticmethod
    def setup(db: Session, machine: Machine, utc_now: datetime) -> None:
        """収集セットアップ開始時の機器、ゲートウェイ、および収集履歴を更新"""

        machine.collect_status = common.COLLECT_STATUS.SETUP.value

        for gateway in machine.gateways:
            gateway.sequence_number += 1
            gateway.status = common.STATUS.RUNNING.value

        new_data_collect_history = DataCollectHistory(
            machine_id=machine.machine_id, machine_name=machine.machine_name, started_at=utc_now, ended_at=None
        )

        db.add(new_data_collect_history)
        db.commit()

    @staticmethod
    def stop(db: Session, machine: Machine) -> None:
        """収集停止時の機器とゲートウェイのステータス更新"""

        machine.collect_status = common.COLLECT_STATUS.STOP.value

        for gateway in machine.gateways:
            gateway.sequence_number += 1
            gateway.status = common.STATUS.STOP.value

        db.commit()

    @staticmethod
    def record(db: Session, machine: Machine, utc_now: datetime) -> None:
        """収集完了時の機器と履歴更新"""

        machine.collect_status = common.COLLECT_STATUS.RECORDED.value

        data_collect_history = (
            db.query(DataCollectHistory)
            .filter(DataCollectHistory.machine_id == machine.machine_id)
            .order_by(desc(DataCollectHistory.started_at))
            .limit(1)
            .one()
        )
        data_collect_history.ended_at = utc_now

        db.commit()
