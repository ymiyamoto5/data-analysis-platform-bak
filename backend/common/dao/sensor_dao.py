from typing import List
from backend.data_collect_manager.models.machine import Machine
from backend.data_collect_manager.models.gateway import Gateway
from backend.data_collect_manager.models.handler import Handler
from backend.data_collect_manager.models.sensor import Sensor
from backend.data_collect_manager.models.sensor_type import SensorType
from backend.common.dao.create_session import db_session
from backend.common.common_logger import logger  # noqa


class SensorDAO:
    @staticmethod
    def select_sensors_by_machine_id(machine_id: str) -> List[Sensor]:
        with db_session() as db:
            sensors: List[Sensor] = (
                db.query(Machine, Gateway, Handler, Sensor, SensorType)
                .filter(Machine.machine_id == machine_id)
                .filter(Machine.machine_id == Gateway.machine_id)
                .filter(Gateway.gateway_id == Handler.gateway_id)
                .filter(Handler.handler_id == Sensor.handler_id)
                .filter(Sensor.sensor_type_id == SensorType.sensor_type_id)
                .all()
            )

        return sensors
