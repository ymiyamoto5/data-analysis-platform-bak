from typing import Any, Dict, List, Union

from backend.app.crud.crud_handler import CRUDHandler
from backend.app.crud.crud_machine import CRUDMachine
from backend.app.models.gateway import Gateway
from backend.app.models.handler import Handler
from backend.app.models.machine import Machine
from backend.app.models.sensor import Sensor
from backend.app.schemas import sensor
from backend.common import common
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload


class CRUDSensor:
    @staticmethod
    def select_all(db: Session) -> List[Sensor]:
        sensors: List[Sensor] = (
            db.query(Sensor)
            .options(
                joinedload(Sensor.sensor_type),
            )
            .all()
        )

        return sensors

    @staticmethod
    def select_by_id(db: Session, machine_id: str, sensor_id: str) -> Sensor:
        sensor: Sensor = (
            db.query(Sensor)
            .options(
                joinedload(Sensor.sensor_type),
            )
            .get((machine_id, sensor_id))
        )

        return sensor

    @staticmethod
    def insert(db: Session, obj_in: sensor.SensorCreate) -> Sensor:
        """センサー登録
        NOTE: センサー数やセンサーID付与処理はトランザクションになっておらず、同時実行されると不具合が発生する。
        """

        machine: Machine = CRUDSensor.fetch_machine_by_handler_id(db, obj_in.handler_id)
        sensors: List[Sensor] = CRUDMachine.select_sensors_by_machine_id(db, machine.machine_id)
        num_of_sensors: int = len(sensors)

        # NOTE: ストローク変位センサー、パルスセンサーはサフィックス番号を付けない
        if obj_in.sensor_type_id in common.CUT_OUT_SHOT_SENSOR_TYPES:
            sensor_id: str = obj_in.sensor_type_id
        # それ以外のセンサーの場合はサフィックス番号を付ける
        else:
            # machineに紐づく特定sensor_typeのsensor（一番番号が大きいもの）を取得
            tail_sensor = (
                db.query(Machine, Handler, Gateway, Sensor)
                .filter(Machine.machine_id == machine.machine_id)
                .filter(Machine.machine_id == Gateway.machine_id)
                .filter(Gateway.gateway_id == Handler.gateway_id)
                .filter(Handler.handler_id == Sensor.handler_id)
                .filter(Sensor.sensor_type_id == obj_in.sensor_type_id)
                .order_by(desc(Sensor.sensor_id))
                .limit(1)
                .one_or_none()
            )

            # 初登録のセンサーの場合
            if tail_sensor is None:
                sensor_id = obj_in.sensor_type_id + "01"
            # 同種で2つめ以降のセンサーの場合
            else:
                # 'load01' -> '01' -> 1 -> 2 -> 'load02'
                tail_sensor_id_suffix: str = tail_sensor.Sensor.sensor_id[-2:]
                sensor_id_suffix: str = str(int(tail_sensor_id_suffix) + 1).zfill(2)
                sensor_id = obj_in.sensor_type_id + sensor_id_suffix

        new_sensor = Sensor(
            machine_id=machine.machine_id,
            sensor_id=sensor_id,
            sensor_name=obj_in.sensor_name,
            sensor_type_id=obj_in.sensor_type_id,
            handler_id=obj_in.handler_id,
            slope=obj_in.slope,
            intercept=obj_in.intercept,
            sort_order=num_of_sensors,  # 並び順は登録順とする
        )

        # handlerのセンサー数を更新する
        handler: Handler = CRUDHandler.select_by_id(db, obj_in.handler_id)
        handler.sampling_ch_num += 1

        db.add(new_sensor)
        db.commit()
        db.refresh(new_sensor)
        return new_sensor

    @staticmethod
    def update(db: Session, db_obj: Sensor, obj_in: Union[sensor.SensorUpdate, Dict[str, Any]]) -> Sensor:
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
    def delete(db: Session, db_obj: Sensor) -> Sensor:
        db.delete(db_obj)

        # handlerのセンサー数を更新する
        handler: Handler = CRUDHandler.select_by_id(db, db_obj.handler_id)
        handler.sampling_ch_num -= 1

        db.commit()
        return db_obj

    @staticmethod
    def fetch_machine_by_handler_id(db: Session, handler_id: str) -> Machine:
        """handler_idを元にmachineを返す"""

        machine: Machine = db.query(Machine).join(Machine.gateways).join(Gateway.handlers).filter(Handler.handler_id == handler_id).one()

        return machine

    @staticmethod
    def fetch_sensors_by_machine_id(db: Session, machine_id: str) -> List[Sensor]:
        """machine_idに紐づく全センサーを取得する"""

        sensors: List[Sensor] = db.query(Sensor).filter(Sensor.machine_id == machine_id).all()

        return sensors
