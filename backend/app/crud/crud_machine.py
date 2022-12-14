from typing import Any, Dict, List, Union

from backend.app.models.gateway import Gateway
from backend.app.models.handler import Handler
from backend.app.models.machine import Machine
from backend.app.models.sensor import Sensor
from backend.app.schemas import machine
from backend.common import common
from sqlalchemy.orm import Session, joinedload


class CRUDMachine:
    @staticmethod
    def select_all(db: Session) -> List[Machine]:
        machines: List[Machine] = (
            db.query(Machine)
            .options(
                joinedload(Machine.machine_type),
                joinedload(Machine.gateways).joinedload(Gateway.handlers).joinedload(Handler.sensors).joinedload(Sensor.sensor_type),
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
                joinedload(Machine.gateways).joinedload(Gateway.handlers).joinedload(Handler.sensors).joinedload(Sensor.sensor_type),
            )
            .get(machine_id)
        )

        return machine

    @staticmethod
    def insert(db: Session, obj_in: machine.MachineCreate) -> Machine:
        new_machine = Machine(
            machine_id=obj_in.machine_id,
            machine_name=obj_in.machine_name,
            collect_status=common.COLLECT_STATUS.RECORDED.value,
            machine_type_id=obj_in.machine_type_id,
        )
        db.add(new_machine)
        db.commit()
        db.refresh(new_machine)
        return new_machine

    @staticmethod
    def update(db: Session, db_obj: Machine, obj_in: Union[machine.MachineUpdate, Dict[str, Any]]) -> Machine:
        """Machine更新。更新値(obj_in)はObjectの場合とdictの場合がある"""

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        # 更新対象のプロパティをセット
        for key, value in update_data.items():
            setattr(db_obj, key, value)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def delete(db: Session, db_obj: Machine) -> Machine:
        db.delete(db_obj)
        db.commit()
        return db_obj

    @staticmethod
    def select_sensors_by_machine_id(db: Session, machine_id: str) -> List[Sensor]:
        sensors: List[Sensor] = db.query(Sensor).filter(Sensor.machine_id == machine_id).all()

        return sensors
