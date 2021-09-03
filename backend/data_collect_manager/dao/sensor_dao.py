from typing import List
from backend.data_collect_manager.models.handler import Handler
from backend.data_collect_manager.models.sensor import Sensor
from backend.data_collect_manager.models.db import db
from backend.data_collect_manager.dao.handler_dao import HandlerDAO
from sqlalchemy.orm import joinedload


class SensorDAO:
    @staticmethod
    def select_all() -> List[Sensor]:
        sensors: List[Sensor] = Sensor.query.options(
            joinedload(Sensor.sensor_type),
        ).all()

        return sensors

    @staticmethod
    def select_by_id(sensor_id: int) -> Sensor:
        sensor: Sensor = Sensor.query.options(
            joinedload(Sensor.sensor_type),
        ).get(sensor_id)

        return sensor

    @staticmethod
    def insert(insert_data: dict) -> None:
        new_sensor = Sensor(
            sensor_name=insert_data["sensor_name"],
            sensor_type_id=insert_data["sensor_type_id"],
            handler_id=insert_data["handler_id"],
        )  # type: ignore

        db.session.add(new_sensor)
        db.session.commit()

    @staticmethod
    def update(sensor_id: int, update_data: dict) -> None:
        # 更新対象取得
        sensor = SensorDAO.select_by_id(sensor_id)

        # 更新対象のプロパティをセット
        for key, value in update_data.items():
            setattr(sensor, key, value)

        db.session.commit()

    @staticmethod
    def delete(sensor_id: int) -> None:
        Sensor.query.filter_by(id=sensor_id).delete()

        db.session.commit()
