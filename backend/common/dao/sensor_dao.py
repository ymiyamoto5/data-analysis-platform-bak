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
            sensors: List[Sensor] = db.query(Sensor).filter(Sensor.machine_id == machine_id).all()

        return sensors
