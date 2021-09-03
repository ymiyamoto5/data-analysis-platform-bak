from typing import List
from backend.data_collect_manager.models.gateway import Gateway
from backend.data_collect_manager.models.handler import Handler
from backend.data_collect_manager.models.sensor import Sensor
from backend.data_collect_manager.models.db import db
from backend.data_collect_manager.dao.gateway_dao import GatewayDAO
from sqlalchemy.orm import joinedload, lazyload


class HandlerDAO:
    @staticmethod
    def select_all() -> List[Handler]:
        handlers: List[Handler] = Handler.query.options(
            joinedload(Handler.sensors).joinedload(Sensor.sensor_type),
        ).all()

        return handlers

    @staticmethod
    def select_by_id(handler_id: str) -> Handler:
        handler: Handler = Handler.query.options(
            joinedload(Handler.sensors).joinedload(Sensor.sensor_type),
        ).get(handler_id)

        return handler

    @staticmethod
    def insert(insert_data: dict) -> None:
        new_handler = Handler(
            handler_id=insert_data["handler_id"],
            adc_serial_num=insert_data["adc_serial_num"],
            handler_type=insert_data["handler_type"],
            sampling_frequency=insert_data["sampling_frequency"],
            sampling_ch_num=insert_data["sampling_ch_num"],
            filewrite_time=insert_data["filewrite_time"],
            gateway_id=insert_data["gateway_id"],
            sensors=[],
        )

        db.session.add(new_handler)
        db.session.commit()

    @staticmethod
    def update(handler_id: str, update_data: dict) -> None:
        # 更新対象取得
        handler = (
            Handler.query.options(lazyload(Handler.sensors))
            .filter(Handler.handler_id == handler_id)
            .with_for_update()
            .one()
        )

        # 更新対象のプロパティをセット
        for key, value in update_data.items():
            setattr(handler, key, value)

        db.session.commit()

    @staticmethod
    def delete(handler_id: str) -> None:
        Handler.query.filter_by(handler_id=handler_id).delete()

        db.session.commit()
