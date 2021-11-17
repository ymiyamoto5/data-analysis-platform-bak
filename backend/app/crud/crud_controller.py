from datetime import datetime
from typing import List

from backend.app.crud.crud_data_collect_history import CRUDDataCollectHistory
from backend.app.crud.crud_data_collect_history_event import CRUDDataCollectHistoryEvent
from backend.app.crud.crud_machine import CRUDMachine
from backend.app.models.data_collect_history import DataCollectHistory
from backend.app.models.data_collect_history_detail import DataCollectHistoryDetail
from backend.app.models.data_collect_history_event import DataCollectHistoryEvent
from backend.app.models.handler import Handler
from backend.app.models.machine import Machine
from backend.app.models.sensor import Sensor
from backend.common import common
from sqlalchemy import desc
from sqlalchemy.orm import Session


class CRUDController:
    @staticmethod
    def setup(db: Session, machine: Machine, utc_now: datetime) -> None:
        """収集セットアップ開始時の機器、ゲートウェイ、収集履歴、および収集イベントを更新"""

        machine.collect_status = common.COLLECT_STATUS.SETUP.value

        for gateway in machine.gateways:
            gateway.sequence_number += 1
            gateway.status = common.STATUS.RUNNING.value

        # 収集履歴更新
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
            sample_count=0,
        )

        db.add(new_data_collect_history)
        db.flush()

        sensors: List[Sensor] = CRUDMachine.select_sensors_by_machine_id(db, machine.machine_id)

        # 収集時のスナップショット
        for sensor in sensors:
            new_data_collect_history_detail = DataCollectHistoryDetail(
                data_collect_history_id=new_data_collect_history.id,
                sensor_id=sensor.sensor_id,
                sensor_name=sensor.sensor_name,
                sensor_type_id=sensor.sensor_type_id,
                slope=sensor.slope,
                intercept=sensor.intercept,
            )
            db.add(new_data_collect_history_detail)

        # 収集イベント更新
        event = DataCollectHistoryEvent(
            data_collect_history_id=new_data_collect_history.id,
            event_id=0,
            event_name=common.COLLECT_STATUS.SETUP.value,
            occurred_at=utc_now,
        )
        db.add(event)
        db.commit()

    @staticmethod
    def start(db: Session, machine: Machine, utc_now: datetime) -> None:
        """収集セットアップ開始時の機器、収集イベントを更新"""

        machine.collect_status = common.COLLECT_STATUS.START.value

        latest_data_collect_history = CRUDDataCollectHistory.select_by_machine_id(db, machine.machine_id)[0]

        num_of_event: int = CRUDDataCollectHistoryEvent.count_by_history_id(db, latest_data_collect_history.id)

        event = DataCollectHistoryEvent(
            data_collect_history_id=latest_data_collect_history.id,
            event_id=num_of_event,
            event_name=common.COLLECT_STATUS.START.value,
            occurred_at=utc_now,
        )
        db.add(event)
        db.commit()

    @staticmethod
    def pause(db: Session, machine: Machine, utc_now: datetime) -> None:
        """収集セットアップ中断時の機器、収集イベントを更新"""

        machine.collect_status = common.COLLECT_STATUS.PAUSE.value

        latest_data_collect_history = CRUDDataCollectHistory.select_by_machine_id(db, machine.machine_id)[0]

        num_of_event: int = CRUDDataCollectHistoryEvent.count_by_history_id(db, latest_data_collect_history.id)

        event = DataCollectHistoryEvent(
            data_collect_history_id=latest_data_collect_history.id,
            event_id=num_of_event,
            event_name=common.COLLECT_STATUS.PAUSE.value,
            occurred_at=utc_now,
        )
        db.add(event)
        db.commit()

    @staticmethod
    def resume(db: Session, machine: Machine, utc_now: datetime) -> None:
        """収集セットアップ再開時の機器、収集イベントを更新"""

        machine.collect_status = common.COLLECT_STATUS.START.value

        latest_data_collect_history = CRUDDataCollectHistory.select_by_machine_id(db, machine.machine_id)[0]

        latest_data_collect_history_event = CRUDDataCollectHistoryEvent.select_latest_by_history_id(db, latest_data_collect_history.id)

        latest_data_collect_history_event.ended_at = utc_now

        db.add(latest_data_collect_history_event)
        db.commit()

    @staticmethod
    def stop(db: Session, machine: Machine, utc_now: datetime) -> None:
        """収集停止時の機器とゲートウェイのステータス、収集イベントを更新"""

        machine.collect_status = common.COLLECT_STATUS.STOP.value

        for gateway in machine.gateways:
            gateway.sequence_number += 1
            gateway.status = common.STATUS.STOP.value

        latest_data_collect_history = CRUDDataCollectHistory.select_by_machine_id(db, machine.machine_id)[0]

        num_of_event: int = CRUDDataCollectHistoryEvent.count_by_history_id(db, latest_data_collect_history.id)

        event = DataCollectHistoryEvent(
            data_collect_history_id=latest_data_collect_history.id,
            event_id=num_of_event,
            event_name=common.COLLECT_STATUS.STOP.value,
            occurred_at=utc_now,
        )
        db.add(event)
        db.commit()

    @staticmethod
    def record(db: Session, machine: Machine, utc_now: datetime) -> None:
        """収集完了時の機器と履歴、収集イベント更新"""

        machine.collect_status = common.COLLECT_STATUS.RECORDED.value

        data_collect_history = (
            db.query(DataCollectHistory)
            .filter(DataCollectHistory.machine_id == machine.machine_id)
            .order_by(desc(DataCollectHistory.started_at))
            .limit(1)
            .one()
        )
        data_collect_history.ended_at = utc_now

        latest_data_collect_history = CRUDDataCollectHistory.select_by_machine_id(db, machine.machine_id)[0]

        num_of_event: int = CRUDDataCollectHistoryEvent.count_by_history_id(db, latest_data_collect_history.id)

        event = DataCollectHistoryEvent(
            data_collect_history_id=latest_data_collect_history.id,
            event_id=num_of_event,
            event_name=common.COLLECT_STATUS.RECORDED.value,
            occurred_at=utc_now,
        )
        db.add(event)
        db.commit()

    @staticmethod
    def reset(db: Session, machine: Machine, utc_now: datetime) -> None:
        """データ収集開始前の状態に更新"""

        machine.collect_status = common.COLLECT_STATUS.RECORDED.value

        for gateway in machine.gateways:
            gateway.sequence_number += 1
            gateway.status = common.STATUS.STOP.value

        data_collect_history = (
            db.query(DataCollectHistory)
            .filter(DataCollectHistory.machine_id == machine.machine_id)
            .order_by(desc(DataCollectHistory.started_at))
            .limit(1)
            .one()
        )
        data_collect_history.ended_at = utc_now

        latest_data_collect_history = CRUDDataCollectHistory.select_by_machine_id(db, machine.machine_id)[0]

        num_of_event: int = CRUDDataCollectHistoryEvent.count_by_history_id(db, latest_data_collect_history.id)

        event = DataCollectHistoryEvent(
            data_collect_history_id=latest_data_collect_history.id,
            event_id=num_of_event,
            event_name=common.COLLECT_STATUS.RECORDED.value,
            occurred_at=utc_now,
        )
        db.add(event)
        db.commit()
