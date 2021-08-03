from dataclasses import dataclass
from data_collect_manager.models.db import db
from data_collect_manager.models.gateway_handler_mapping import GatewayHandlerMapping


@dataclass
class Handler(db.Model):
    __tablename__ = "handlers"

    handler_id: str
    handler_type: str
    adc_serial_num: str
    sampling_frequency: int
    sampling_ch_num: int
    filewrite_time: int

    handler_id = db.Column(db.String(255), primary_key=True)
    handler_type = db.Column(db.String(255))
    adc_serial_num = db.Column(db.String(255))
    sampling_frequency = db.Column(db.Integer)
    sampling_ch_num = db.Column(db.Integer)
    filewrite_time = db.Column(db.Integer)

    gateways = db.relationship("Gateway", secondary=GatewayHandlerMapping.__tablename__, back_populates="handlers")
