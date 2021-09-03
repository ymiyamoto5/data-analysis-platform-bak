from typing import List
from backend.data_collect_manager.models.gateway import Gateway
from backend.data_collect_manager.models.handler import Handler
from backend.data_collect_manager.models.sensor import Sensor
from backend.data_collect_manager.models.db import db
from sqlalchemy.orm import joinedload, lazyload
from backend.common import common


class GatewayDAO:
    @staticmethod
    def select_all() -> List[Gateway]:
        gateways: List[Gateway] = Gateway.query.options(
            joinedload(Gateway.handlers).joinedload(Handler.sensors).joinedload(Sensor.sensor_type),
        ).all()

        return gateways

    @staticmethod
    def select_by_id(gateway_id: str) -> Gateway:
        gateway: Gateway = Gateway.query.options(
            joinedload(Gateway.handlers).joinedload(Handler.sensors).joinedload(Sensor.sensor_type),
        ).get(gateway_id)

        return gateway

    @staticmethod
    def insert(insert_data: dict) -> None:
        new_gateway = Gateway(
            gateway_id=insert_data["gateway_id"],
            sequence_number=1,
            gateway_result=0,
            status=common.STATUS.STOP.value,
            log_level=insert_data["log_level"],
            machine_id=insert_data["machine_id"],
            handlers=[],
        )

        db.session.add(new_gateway)
        db.session.commit()

    @staticmethod
    def update(gateway_id: str, update_data: dict) -> None:
        # 更新対象取得
        gateway = (
            Gateway.query.options(lazyload(Gateway.handlers))
            .filter(Gateway.gateway_id == gateway_id)
            .with_for_update()
            .one()
        )

        # 更新対象のプロパティをセット
        for key, value in update_data.items():
            setattr(gateway, key, value)

        db.session.commit()

    @staticmethod
    def delete(gateway_id: str) -> None:
        Gateway.query.filter_by(gateway_id=gateway_id).delete()

        db.session.commit()
