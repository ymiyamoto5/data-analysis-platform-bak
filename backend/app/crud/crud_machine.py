from typing import List
from backend.app.models.machine import Machine
from backend.app.models.gateway import Gateway
from backend.app.models.handler import Handler
from backend.app.models.sensor import Sensor
from sqlalchemy.orm import joinedload, lazyload
from backend.common import common
from sqlalchemy.orm import Session
from backend.app.schemas import machine


class CRUDMachine:
    @staticmethod
    def select_all(db: Session) -> List[Machine]:
        machines: List[Machine] = (
            db.query(Machine)
            .options(
                joinedload(Machine.machine_type),
                joinedload(Machine.gateways)
                .joinedload(Gateway.handlers)
                .joinedload(Handler.sensors)
                .joinedload(Sensor.sensor_type),
            )
            .all()
        )

        return machines

    @staticmethod
    def select_by_id(db: Session, machine_id: str) -> Machine:
        machine: Machine = (
            db.query(Machine)
            .options(
                joinedload(Machine.machine_type),
                joinedload(Machine.gateways)
                .joinedload(Gateway.handlers)
                .joinedload(Handler.sensors)
                .joinedload(Sensor.sensor_type),
            )
            .get(machine_id)
        )

        return machine

    @staticmethod
    def insert(db: Session, insert_data: machine.MachineCreate) -> Machine:
        new_machine = Machine(
            machine_id=insert_data.machine_id,
            machine_name=insert_data.machine_name,
            collect_status=common.COLLECT_STATUS.RECORDED.value,
            machine_type_id=insert_data.machine_type_id,
        )
        db.add(new_machine)
        db.commit()
        db.refresh(new_machine)
        return new_machine

    # @staticmethod
    # def update(machine_id: str, update_data: dict) -> None:
    #     # 悲観的排他ロック(sqliteでは無効)
    #     machine = (
    #         Machine.query.options(lazyload(Machine.machine_type), lazyload(Machine.gateways))
    #         .filter(Machine.machine_id == machine_id)
    #         .with_for_update()
    #         .one()
    #     )

    #     # 更新対象のプロパティをセット
    #     for key, value in update_data.items():
    #         setattr(machine, key, value)

    #     db.session.commit()

    # @staticmethod
    # def delete(machine_id: str) -> None:
    #     Machine.query.filter_by(machine_id=machine_id).delete()

    #     db.session.commit()
