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
    def select_by_id(sensor_id: str) -> Sensor:
        sensor: Sensor = Sensor.query.options(
            joinedload(Sensor.sensor_type),
        ).get(sensor_id)

        return sensor

    @staticmethod
    def insert(insert_data: dict) -> None:
        # Sensorに紐づくHandler
        handlers: List[Handler] = Handler.query.filter_by(handler_id=insert_data["handler_id"]).all()

        new_sensor = Sensor(
            sensor_id=insert_data["sensor_id"],
            sensor_name=insert_data["sensor_name"],
            sensor_type_id=insert_data["sensor_type_id"],
            handlers=handlers,
        )  # type: ignore

        db.session.add(new_sensor)
        db.session.commit()

    @staticmethod
    def update(sensor_id: str, update_data: dict) -> None:
        # 更新対象取得
        sensor = SensorDAO.select_by_id(sensor_id)

        # Sensorに紐づくHandlerの更新
        if "handler_id" in update_data:
            handler: Handler = HandlerDAO.select_by_id(update_data["handler_id"])
            if handler is None:
                raise Exception("related handler does not exist.")
            sensor.handlers.append(handler)

        # 更新対象のプロパティをセット
        for key, value in update_data.items():
            setattr(sensor, key, value)

        db.session.commit()

    @staticmethod
    def delete(sensor_id: str) -> None:
        Sensor.query.filter_by(sensor_id=sensor_id).delete()

        db.session.commit()
