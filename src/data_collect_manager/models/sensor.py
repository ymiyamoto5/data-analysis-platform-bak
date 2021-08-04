from dataclasses import dataclass
from data_collect_manager.models.db import db
from data_collect_manager.models.handler_sensor_mapping import HandlerSensorMapping


@dataclass
class Sensor(db.Model):
    __tablename__ = "sensors"

    id: int
    sensor_name: str
    sensor_type_id: int

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sensor_name = db.Column(db.String(255), nullable=False)
    sensor_type_id = db.Column(db.Integer, db.ForeignKey("sensor_types.id"))

    handlers = db.relationship("Handler", secondary=HandlerSensorMapping.__tablename__, back_populates="sensors")
    # sensor_type = db.relationship("SensorType", back_populates="sensors")
