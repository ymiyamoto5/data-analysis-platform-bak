from typing import List
from backend.data_collect_manager.models.machine import Machine
from backend.data_collect_manager.models.gateway import Gateway
from backend.data_collect_manager.models.handler import Handler
from backend.data_collect_manager.models.sensor import Sensor
from backend.data_collect_manager.models.db import db
from backend.data_collect_manager.dao.machine_dao import MachineDAO
from sqlalchemy.orm import joinedload
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
    def insert(gateway_id: str, log_level: int, machine_id: str = None) -> None:

        if machine_id is not None:
            machines: List[Machine] = Machine.query.filter_by(machine_id=machine_id).all()
        else:
            machines = []

        new_gateway = Gateway(
            gateway_id=gateway_id,
            sequence_number=1,
            gateway_result=0,
            status=common.STATUS.STOP.value,
            log_level=log_level,
            machines=machines,
        )  # type: ignore

        db.session.add(new_gateway)
        db.session.commit()

    @staticmethod
    def update(gateway_id: str, update_data: dict) -> None:
        gateway = GatewayDAO.select_by_id(gateway_id)

        if "machine_id" in update_data:
            machine: Machine = MachineDAO.select_by_id(update_data["machine_id"])
            gateway.machines.append(machine)

        # 更新対象のプロパティをセット
        for key, value in update_data.items():
            setattr(gateway, key, value)

        db.session.commit()

    @staticmethod
    def delete(gateway_id: str) -> None:
        Gateway.query.filter_by(gateway_id=gateway_id).delete()

        db.session.commit()
