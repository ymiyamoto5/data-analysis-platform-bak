from dataclasses import dataclass
from data_collect_manager.models.db import db
from data_collect_manager.models.gateway_handler_mapping import GatewayHandlerMapping


@dataclass
class Handler(db.Model):
    __tablename__ = "handlers"

    id: int
    handler_name: str
    handler_type: str
    adc_serial_num: str
    sampling_frequency: int
    sampling_ch_num: int
    filewrite_time: int

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    handler_name = db.Column(db.String(255), unique=True, nullable=False)
    handler_type = db.Column(db.String(255))
    adc_serial_num = db.Column(db.String(255))
    sampling_frequency = db.Column(db.Integer)
    sampling_ch_num = db.Column(db.Integer)
    filewrite_time = db.Column(db.Integer)

    gateways = db.relationship("Gateway", secondary=GatewayHandlerMapping.__tablename__, back_populates="handlers")
