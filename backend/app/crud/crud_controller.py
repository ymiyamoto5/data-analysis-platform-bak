from datetime import datetime

from backend.app.crud.crud_data_collect_history import CRUDDataCollectHistory
from backend.app.crud.crud_data_collect_history_event import CRUDDataCollectHistoryEvent
from backend.app.models.data_collect_history import DataCollectHistory
from backend.app.models.data_collect_history_event import DataCollectHistoryEvent
from backend.app.models.data_collect_history_gateway import DataCollectHistoryGateway
from backend.app.models.data_collect_history_handler import DataCollectHistoryHandler
from backend.app.models.data_collect_history_sensor import DataCollectHistorySensor
from backend.app.models.machine import Machine
from backend.common import common
from sqlalchemy.orm import Session


class CRUDController:
    @staticmethod
    def setup(db: Session, machine: Machine, utc_now: datetime, processed_dir_path: str) -> None:
        """収集セットアップ開始時の機器、ゲートウェイ、収集履歴、および収集イベントを更新"""

        machine.collect_status = common.COLLECT_STATUS.SETUP.value

        for gateway in machine.gateways:
            gateway.sequence_number = common.increment_sequence_number(gateway.sequence_number)
            gateway.status = common.STATUS.RUNNING.value

        # 収集時のスナップショットを履歴として保存
        new_data_collect_history = DataCollectHistory(
            machine_id=machine.machine_id,
            machine_name=machine.machine_name,
            machine_type_id=machine.machine_type_id,
            started_at=utc_now,
            ended_at=None,
            processed_dir_path=processed_dir_path,
        )
        db.add(new_data_collect_history)
        db.flush()

        for gateway in machine.gateways:
            new_data_collect_history_gateway = DataCollectHistoryGateway(
                data_collect_history_id=new_data_collect_history.id,
                gateway_id=gateway.gateway_id,
                log_level=gateway.log_level,
            )
            db.add(new_data_collect_history_gateway)
            db.flush()

            for handler in gateway.handlers:
                new_data_collect_history_handler = DataCollectHistoryHandler(
                    data_collect_history_id=new_data_collect_history.id,
                    gateway_id=new_data_collect_history_gateway.gateway_id,
                    handler_id=handler.handler_id,
                    handler_type=handler.handler_type,
                    adc_serial_num=handler.adc_serial_num,
                    sampling_frequency=handler.sampling_frequency,
                    sampling_ch_num=handler.sampling_ch_num,
                    filewrite_time=handler.filewrite_time,
                    is_primary=handler.is_primary,
                    is_cut_out_target=True,
                )
                db.add(new_data_collect_history_handler)
                db.flush()

                for sensor in handler.sensors:
                    new_data_collect_history_sensor = DataCollectHistorySensor(
                        data_collect_history_id=new_data_collect_history.id,
                        gateway_id=new_data_collect_history_gateway.gateway_id,
                        handler_id=new_data_collect_history_handler.handler_id,
                        sensor_id=sensor.sensor_id,
                        sensor_name=sensor.sensor_name,
                        sensor_type_id=sensor.sensor_type_id,
                        slope=sensor.slope,
                        intercept=sensor.intercept,
                        start_point_dsl=sensor.start_point_dsl,
                        max_point_dsl=sensor.max_point_dsl,
                        break_point_dsl=sensor.break_point_dsl,
                    )
                    db.add(new_data_collect_history_sensor)
                    db.flush()

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

        num_of_event: int = len(latest_data_collect_history.data_collect_history_events)

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

        num_of_event: int = len(latest_data_collect_history.data_collect_history_events)

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
            gateway.sequence_number = common.increment_sequence_number(gateway.sequence_number)
            gateway.status = common.STATUS.STOP.value

        latest_data_collect_history = CRUDDataCollectHistory.select_by_machine_id(db, machine.machine_id)[0]

        num_of_event: int = len(latest_data_collect_history.data_collect_history_events)

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

        latest_data_collect_history = CRUDDataCollectHistory.select_latest_by_machine_id(db, machine.machine_id)

        latest_data_collect_history.ended_at = utc_now

        num_of_event: int = len(latest_data_collect_history.data_collect_history_events)

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

        for gateway in machine.gateways:
            gateway.sequence_number = common.increment_sequence_number(gateway.sequence_number)
            gateway.status = common.STATUS.STOP.value

        # 段取開始前にリセットした場合はゲートウェイのみ更新
        if machine.collect_status == common.COLLECT_STATUS.RECORDED.value:
            db.commit()
            return

        # 段取開始後にリセットした場合は履歴とイベントも更新
        machine.collect_status = common.COLLECT_STATUS.RECORDED.value

        latest_data_collect_history = CRUDDataCollectHistory.select_by_machine_id(db, machine.machine_id)[0]

        latest_data_collect_history.ended_at = utc_now

        num_of_event: int = len(latest_data_collect_history.data_collect_history_events)

        event = DataCollectHistoryEvent(
            data_collect_history_id=latest_data_collect_history.id,
            event_id=num_of_event,
            event_name=common.COLLECT_STATUS.RECORDED.value,
            occurred_at=utc_now,
        )
        db.add(event)
        db.commit()
