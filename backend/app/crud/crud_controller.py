from typing import List
from datetime import datetime
from sqlalchemy import desc
from backend.app.models.machine import Machine
from backend.app.models.handler import Handler
from backend.app.models.sensor import Sensor
from backend.app.models.data_collect_history import DataCollectHistory
from backend.app.models.data_collect_history_detail import DataCollectHistoryDetail
from backend.app.crud.crud_machine import CRUDMachine
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

        # NOTE: 複数GW, 複数Handlerであっても、最初のGWおよびそれに紐づく最初のHandlerを採用する。
        handler: Handler = machine.gateways[0].handlers[0]

        new_data_collect_history = DataCollectHistory(
            machine_id=machine.machine_id,
            machine_name=machine.machine_name,
            machine_type_id=machine.machine_type_id,
            started_at=utc_now,
            ended_at=None,
            sampling_frequency=handler.sampling_frequency,
            sampling_ch_num=handler.sampling_ch_num,
        )

        db.add(new_data_collect_history)
        db.commit()

        sensors: List[Sensor] = CRUDMachine.select_sensors_by_machine_id(db, machine.machine_id)

        for sensor in sensors:
            new_data_collect_history_detail = DataCollectHistoryDetail(
                data_collect_history_id=new_data_collect_history.id,
                sensor_id=sensor.sensor_id,
                sensor_name=sensor.sensor_name,
                sensor_type_id=sensor.sensor_type_id,
                base_volt=sensor.base_volt,
                base_load=sensor.base_load,
                initial_volt=sensor.initial_volt,
            )
            db.add(new_data_collect_history_detail)

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
