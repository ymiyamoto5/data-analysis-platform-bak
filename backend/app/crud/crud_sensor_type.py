from typing import List
from backend.app.models.sensor_type import SensorType
from sqlalchemy.orm import Session


class CRUDSensorType:
    @staticmethod
    def select_all(db: Session) -> List[SensorType]:
        sensor_types: List[SensorType] = db.query(SensorType).all()

        return sensor_types
