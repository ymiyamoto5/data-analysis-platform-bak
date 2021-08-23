from dataclasses import dataclass
from backend.data_collect_manager.models.db import db
from backend.data_collect_manager.models.sensor_type import SensorType
from backend.data_collect_manager.models.handler_sensor_mapping import HandlerSensorMapping


@dataclass
class Sensor(db.Model):
    __tablename__ = "sensors"

    id: int
    sensor_name: str
    sensor_type_id: int
    # NOTE: SensorからSensorTypeを引くためのプロパティ
    sensor_type: SensorType

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sensor_name = db.Column(db.String(255), nullable=False)
    sensor_type_id = db.Column(db.Integer, db.ForeignKey("sensor_types.id"))

    handlers = db.relationship(
        "Handler", secondary=HandlerSensorMapping.__tablename__, back_populates="sensors", passive_deletes=True
    )
    # NOTE: SensorとSensorTypeはMany to One
    sensor_type = db.relationship("SensorType", back_populates="sensors")
