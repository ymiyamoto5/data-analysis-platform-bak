from dataclasses import dataclass
from backend.data_collect_manager.models.db import db
from backend.data_collect_manager.models.sensor_type import SensorType


@dataclass
class Sensor(db.Model):
    __tablename__ = "sensors"

    sensor_id: str
    sensor_name: str
    sensor_type_id: str
    # NOTE: SensorからSensorTypeを引くためのプロパティ
    sensor_type: SensorType
    handler_id: str
    # NOTE: 冗長なリレーションシップとなるが、複合主キー（機器ごとに一意のセンサー）とするため必要。
    machine_id: str

    machine_id = db.Column(db.String(255), db.ForeignKey("machines.machine_id"), primary_key=True)
    sensor_id = db.Column(db.String(255), primary_key=True)
    sensor_name = db.Column(db.String(255), nullable=False)
    sensor_type_id = db.Column(db.String(255), db.ForeignKey("sensor_types.sensor_type_id"), nullable=False)
    handler_id = db.Column(db.String(255), db.ForeignKey("handlers.handler_id"), nullable=False)

    # NOTE: SensorとMachineはMany to One
    # machine = db.relationship("Machine", back_populates="machines")
    # NOTE: SensorとHandlerはMany to One
    handler = db.relationship("Handler", back_populates="sensors")
    # NOTE: SensorとSensorTypeはMany to One
    sensor_type = db.relationship("SensorType", back_populates="sensors")
