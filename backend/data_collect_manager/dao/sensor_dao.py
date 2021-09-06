from typing import List
from backend.data_collect_manager.models.machine import Machine
from backend.data_collect_manager.models.gateway import Gateway
from backend.data_collect_manager.models.handler import Handler
from backend.data_collect_manager.models.sensor import Sensor
from backend.data_collect_manager.models.db import db
from sqlalchemy.orm import joinedload
from sqlalchemy import desc


class SensorDAO:
    @staticmethod
    def select_all() -> List[Sensor]:
        sensors: List[Sensor] = Sensor.query.options(
            joinedload(Sensor.sensor_type),
        ).all()

        return sensors

    @staticmethod
    def select_by_id(machine_id: str, sensor_id: str) -> Sensor:
        sensor: Sensor = Sensor.query.options(
            joinedload(Sensor.sensor_type),
        ).get((machine_id, sensor_id))

        return sensor

    @staticmethod
    def insert(insert_data: dict) -> None:
        handler_id: str = insert_data["handler_id"]
        machine_id: str = SensorDAO.fetch_machine_by_handler_id(handler_id)
        sensor_type_id: str = insert_data["sensor_type_id"]

        # machineに紐づく特定sensor_typeのsensor（一番番号が大きいもの）を取得
        tail_sensor = (
            db.session.query(Machine, Handler, Gateway, Sensor)
            .filter(Machine.machine_id == machine_id)
            .filter(Machine.machine_id == Gateway.machine_id)
            .filter(Gateway.gateway_id == Handler.gateway_id)
            .filter(Handler.handler_id == Sensor.handler_id)
            .filter(Sensor.sensor_type_id == sensor_type_id)
            .order_by(desc(Sensor.sensor_id))
            .limit(1)
            .one_or_none()
        )

        # Sensor名設定
        # 初登録のセンサーの場合
        if tail_sensor is None:
            sensor_id: str = sensor_type_id + "01"
        # 2つめ移行のセンサーの場合
        else:
            # 'load01' -> '01' -> 1 -> 2 -> 'load02'
            tail_sensor_id_suffix: str = tail_sensor.Sensor.sensor_id[-2:]
            sensor_id_suffix: str = str(int(tail_sensor_id_suffix) + 1).zfill(2)
            sensor_id = sensor_type_id + sensor_id_suffix

        new_sensor = Sensor(
            machine_id=machine_id,
            sensor_id=sensor_id,
            sensor_name=insert_data["sensor_name"],
            sensor_type_id=sensor_type_id,
            handler_id=handler_id,
        )  # type: ignore

        db.session.add(new_sensor)
        db.session.commit()

    @staticmethod
    def update(sensor_id: str, update_data: dict) -> None:
        handler_id: str = update_data["handler_id"]
        machine_id: str = SensorDAO.fetch_machine_by_handler_id(handler_id)

        # 更新対象取得
        sensor = SensorDAO.select_by_id(machine_id, sensor_id)

        # 更新対象のプロパティをセット
        for key, value in update_data.items():
            setattr(sensor, key, value)

        db.session.commit()

    @staticmethod
    def delete(sensor_id: str, delete_data: dict) -> None:
        handler_id: str = delete_data["handler_id"]
        machine_id: str = SensorDAO.fetch_machine_by_handler_id(handler_id)

        Sensor.query.filter_by(machine_id=machine_id, sensor_id=sensor_id).delete()

        db.session.commit()

    @staticmethod
    def fetch_machine_by_handler_id(handler_id: str) -> str:
        """handler_idを元にmachine_idを返す"""
        joined = (
            db.session.query(Handler, Gateway, Machine)
            .filter(Handler.handler_id == handler_id)
            .filter(Gateway.gateway_id == Handler.gateway_id)
            .filter(Machine.machine_id == Gateway.machine_id)
            .one()
        )

        machine_id: str = joined.Machine.machine_id

        return machine_id
