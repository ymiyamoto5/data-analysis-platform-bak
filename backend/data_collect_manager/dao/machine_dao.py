from typing import List
from backend.data_collect_manager.models.machine import Machine
from backend.data_collect_manager.models.gateway import Gateway
from backend.data_collect_manager.models.handler import Handler
from backend.data_collect_manager.models.sensor import Sensor
from backend.data_collect_manager.models.db import db
from sqlalchemy.orm import joinedload, lazyload
from backend.common import common


class MachineDAO:
    @staticmethod
    def select_all() -> List[Machine]:
        machines: List[Machine] = Machine.query.options(
            joinedload(Machine.machine_type),
            joinedload(Machine.gateways)
            .joinedload(Gateway.handlers)
            .joinedload(Handler.sensors)
            .joinedload(Sensor.sensor_type),
        ).all()

        return machines

    @staticmethod
    def select_by_id(machine_id: str) -> Machine:
        machine: Machine = Machine.query.options(
            joinedload(Machine.machine_type),
            joinedload(Machine.gateways)
            .joinedload(Gateway.handlers)
            .joinedload(Handler.sensors)
            .joinedload(Sensor.sensor_type),
        ).get(machine_id)

        return machine

    @staticmethod
    def insert(insert_data: dict) -> None:
        # NOTE: 型エラー回避のためにmachine_type = None等を設定することはできないため、type: ignoreしている。
        new_machine = Machine(
            machine_id=insert_data["machine_id"],
            machine_name=insert_data["machine_name"],
            collect_status=common.COLLECT_STATUS.RECORDED.value,
            machine_type_id=insert_data["machine_type_id"],
        )  # type: ignore

        db.session.add(new_machine)
        db.session.commit()

    @staticmethod
    def update(machine_id: str, update_data: dict) -> None:
        # 悲観的排他ロック(sqliteでは無効)
        machine = (
            Machine.query.options(lazyload(Machine.machine_type), lazyload(Machine.gateways))
            .filter(Machine.machine_id == machine_id)
            .with_for_update()
            .one()
        )

        # 更新対象のプロパティをセット
        for key, value in update_data.items():
            setattr(machine, key, value)

        db.session.commit()

    @staticmethod
    def delete(machine_id: str) -> None:
        Machine.query.filter_by(machine_id=machine_id).delete()

        db.session.commit()
