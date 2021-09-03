from dataclasses import dataclass
from backend.data_collect_manager.models.db import db


@dataclass
class SensorType(db.Model):
    __tablename__ = "sensor_types"

    sensor_type_id: str
    sensor_type_name: str

    sensor_type_id = db.Column(db.String(255), primary_key=True)
    sensor_type_name = db.Column(db.String(255), unique=True, nullable=False)

    sensors = db.relationship("Sensor", back_populates="sensor_type")
