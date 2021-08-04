from dataclasses import dataclass
from data_collect_manager.models.db import db


@dataclass
class SensorType(db.Model):
    __tablename__ = "sensor_types"

    id: int
    sensor_type_name: str

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sensor_type_name = db.Column(db.String(255), unique=True, nullable=False)

    sensors = db.relationship("Sensor", back_populates="sensor_type")
