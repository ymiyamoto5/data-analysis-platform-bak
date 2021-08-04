from dataclasses import dataclass
from data_collect_manager.models.db import db
from data_collect_manager.models.gateway_handler_mapping import GatewayHandlerMapping
from data_collect_manager.models.handler_sensor_mapping import HandlerSensorMapping
from data_collect_manager.models.sensor import Sensor


@dataclass
class Handler(db.Model):
    __tablename__ = "handlers"

    handler_id: str
    handler_type: str
    adc_serial_num: str
    sampling_frequency: int
    sampling_ch_num: int
    filewrite_time: int

    sensors: Sensor

    handler_id = db.Column(db.String(255), primary_key=True)
    handler_type = db.Column(db.String(255))
    adc_serial_num = db.Column(db.String(255))
    sampling_frequency = db.Column(db.Integer)
    sampling_ch_num = db.Column(db.Integer)
    filewrite_time = db.Column(db.Integer)

    gateways = db.relationship("Gateway", secondary=GatewayHandlerMapping.__tablename__, back_populates="handlers")
    sensors = db.relationship("Sensor", secondary=HandlerSensorMapping.__tablename__, back_populates="handlers")
