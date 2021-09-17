from typing import List, Dict, Union, Any
from backend.app.models.machine import Machine
from backend.app.models.gateway import Gateway
from backend.app.models.handler import Handler
from backend.app.models.sensor import Sensor
from sqlalchemy.orm import joinedload
from backend.common import common
from sqlalchemy.orm import Session
from backend.app.schemas import machine
from backend.common.db_session import db_session


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
    def fetch_handler_from_machine_id(machine_id: str) -> Handler:
        """DBからmachine_idをkeyにHandler情報を取得する。"""

        with db_session() as db:
            machine: Machine = (
                db.query(Machine)
                .filter(Machine.machine_id == machine_id)
                .join(Gateway, Machine.gateways)
                .join(Handler, Gateway.handlers)
                .one()
            )

            # NOTE: 1つ目のGW, 1つ目のHandlerを採用。複数GW, 複数Handlerには対応していない。
            # NOTE: handlerがない場合はException
            handler: Handler = machine.gateways[0].handlers[0]

        return handler

    @staticmethod
    def select_sensors_by_machine_id(machine_id: str) -> List[Sensor]:
        with db_session() as db:
            sensors: List[Sensor] = db.query(Sensor).filter(Sensor.machine_id == machine_id).all()

        return sensors

    @staticmethod
    def select_machines_has_handler() -> List[Machine]:
        with db_session() as db:
            machines: List[Machine] = (
                db.query(Machine).join(Gateway, Machine.gateways).join(Handler, Gateway.handlers).all()
            )

        return machines
