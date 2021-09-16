from typing import List, Dict, Union, Any
from backend.app.models.gateway import Gateway
from backend.app.models.handler import Handler
from backend.app.models.sensor import Sensor
from sqlalchemy.orm import joinedload
from backend.common import common
from sqlalchemy.orm import Session
from backend.app.schemas import gateway


class CRUDGateway:
    @staticmethod
    def select_all(db: Session) -> List[Gateway]:
        gateways: List[Gateway] = (
            db.query(Gateway)
            .options(
                joinedload(Gateway.handlers).joinedload(Handler.sensors).joinedload(Sensor.sensor_type),
            )
            .all()
        )

        return gateways

    @staticmethod
    def select_by_id(db: Session, gateway_id: str) -> Gateway:
        gateway: Gateway = (
            db.query(Gateway)
            .options(
                joinedload(Gateway.handlers).joinedload(Handler.sensors).joinedload(Sensor.sensor_type),
            )
            .get(gateway_id)
        )

        return gateway

    @staticmethod
    def insert(db: Session, obj_in: gateway.GatewayCreate) -> Gateway:
        new_gateway = Gateway(
            gateway_id=obj_in.gateway_id,
            sequence_number=1,
            gateway_result=0,
            status=common.STATUS.STOP.value,
            log_level=obj_in.log_level,
            machine_id=obj_in.machine_id,
            handlers=[],
        )

        db.add(new_gateway)
        db.commit()
        db.refresh(new_gateway)
        return new_gateway

    @staticmethod
    def update(db: Session, db_obj: Gateway, obj_in: Union[gateway.GatewayUpdate, Dict[str, Any]]) -> Gateway:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        # 更新対象のプロパティをセット
        for key, value in update_data.items():
            setattr(db_obj, key, value)

        # 更新したことをGatewayに知らせるため、gateway_resultを0に設定
        db_obj.gateway_result = 0

        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, db_obj: Gateway) -> Gateway:
        db.delete(db_obj)
        db.commit()
        return db_obj
