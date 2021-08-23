from dataclasses import dataclass
from backend.data_collect_manager.models.db import db
from backend.data_collect_manager.models.machine_gateway_mapping import MachineGatewayMapping
from backend.data_collect_manager.models.gateway_handler_mapping import GatewayHandlerMapping
from backend.data_collect_manager.models.handler import Handler


@dataclass
class Gateway(db.Model):
    __tablename__ = "gateways"

    gateway_id: str
    sequence_number: int
    gateway_result: int
    status: str
    log_level: int

    handlers: Handler

    gateway_id = db.Column(db.String(255), primary_key=True)
    sequence_number = db.Column(db.Integer)
    gateway_result = db.Column(db.Integer)
    status = db.Column(db.String(255))
    log_level = db.Column(db.Integer)

    machines = db.relationship(
        "Machine", secondary=MachineGatewayMapping.__tablename__, back_populates="gateways", passive_deletes=True
    )
    handlers = db.relationship(
        "Handler", secondary=GatewayHandlerMapping.__tablename__, back_populates="gateways", cascade="all, delete"
    )
