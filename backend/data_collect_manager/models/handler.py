from typing import List
from dataclasses import dataclass
from backend.data_collect_manager.models.db import db
from backend.data_collect_manager.models.sensor import Sensor


@dataclass
class Handler(db.Model):
    __tablename__ = "handlers"

    handler_id: str
    handler_type: str
    adc_serial_num: str
    sampling_frequency: int
    sampling_ch_num: int
    filewrite_time: int
    gateway_id: str
    sensors: List[Sensor]

    handler_id = db.Column(db.String(255), primary_key=True)
    handler_type = db.Column(db.String(255))
    adc_serial_num = db.Column(db.String(255))
    sampling_frequency = db.Column(db.Integer)
    sampling_ch_num = db.Column(db.Integer)
    filewrite_time = db.Column(db.Integer)
    gateway_id = db.Column(db.Integer, db.ForeignKey("gateways.gateway_id"), nullable=False)

    gateway = db.relationship("Gateway", back_populates="handlers")
    sensors = db.relationship("Sensor", back_populates="handler", cascade="all, delete")
