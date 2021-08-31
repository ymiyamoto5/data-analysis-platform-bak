from datetime import datetime
from sqlalchemy import desc
from backend.data_collect_manager.models.machine import Machine
from backend.data_collect_manager.models.data_collect_history import DataCollectHistory
from backend.data_collect_manager.models.db import db
from backend.common import common


class ControlerDAO:
    @staticmethod
    def setup(machine: Machine, utc_now: datetime) -> None:
        """収集セットアップ開始時の機器、ゲートウェイ、および収集履歴を更新"""

        machine.collect_status = common.COLLECT_STATUS.SETUP.value

        for gateway in machine.gateways:
            gateway.sequence_number += 1
            gateway.status = common.STATUS.RUNNING.value

        new_data_collect_history = DataCollectHistory(
            machine_id=machine.machine_id, machine_name=machine.machine_name, started_at=utc_now, ended_at=None
        )  # type: ignore

        db.session.add(new_data_collect_history)
        db.session.commit()

    @staticmethod
    def stop(machine: Machine) -> None:
        """収集停止時の機器とゲートウェイのステータス更新"""

        machine.collect_status = common.COLLECT_STATUS.STOP.value

        for gateway in machine.gateways:
            gateway.sequence_number += 1
            gateway.status = common.STATUS.STOP.value

        db.session.commit()

    @staticmethod
    def record(machine: Machine, utc_now: datetime) -> None:
        """収集完了時の機器と履歴更新"""

        machine.collect_status = common.COLLECT_STATUS.RECORDED.value

        data_collect_history = (
            DataCollectHistory.query.filter(DataCollectHistory.machine_id == machine.machine_id)
            .order_by(desc(DataCollectHistory.started_at))
            .limit(1)
            .one()
        )
        data_collect_history.ended_at = utc_now

        db.session.commit()
