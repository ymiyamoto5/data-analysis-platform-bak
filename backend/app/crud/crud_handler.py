from typing import Any, Dict, List, Union

from backend.app.crud.crud_gateway import CRUDGateway
from backend.app.models.handler import Handler
from backend.app.models.sensor import Sensor
from backend.app.schemas import handler
from sqlalchemy.orm import Session, joinedload


class CRUDHandler:
    @staticmethod
    def select_all(db: Session) -> List[Handler]:
        handlers: List[Handler] = (
            db.query(Handler)
            .options(
                joinedload(Handler.sensors).joinedload(Sensor.sensor_type),
            )
            .all()
        )

        return handlers

    @staticmethod
    def select_by_id(db: Session, handler_id: str) -> Handler:
        handler: Handler = (
            db.query(Handler)
            .options(
                joinedload(Handler.sensors).joinedload(Sensor.sensor_type),
            )
            .get(handler_id)
        )

        return handler

    @staticmethod
    def insert(db: Session, obj_in: handler.HandlerCreate) -> Handler:
        new_handler = Handler(
            handler_id=obj_in.handler_id,
            adc_serial_num=obj_in.adc_serial_num,
            handler_type=obj_in.handler_type,
            sampling_frequency=obj_in.sampling_frequency,
            sampling_ch_num=0,
            filewrite_time=obj_in.filewrite_time,
            gateway_id=obj_in.gateway_id,
        )

        # Handlerを更新したことをGatewayに知らせるため、gateway_resultを0に設定
        gateway = CRUDGateway.select_by_id(db, obj_in.gateway_id)
        gateway.gateway_result = 0

        db.add(new_handler)
        db.commit()
        db.refresh(new_handler)
        return new_handler

    @staticmethod
    def update(db: Session, db_obj: Handler, obj_in: Union[handler.HandlerUpdate, Dict[str, Any]]) -> Handler:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        # 更新対象のプロパティをセット
        for key, value in update_data.items():
            setattr(db_obj, key, value)

        # 更新したことをGatewayに知らせるため、sequence_numberをインクリメントし、gateway_resultを0に設定
        db_obj.gateway.sequence_number += 1
        db_obj.gateway.gateway_result = 0

        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, db_obj: Handler) -> Handler:
        db.delete(db_obj)
        db.commit()
        return db_obj
