from dataclasses import dataclass
from data_collect_manager.models.db import db
from data_collect_manager.models.machine_gateway_mapping import MachineGatewayMapping


@dataclass
class Gateway(db.Model):
    __tablename__ = "gateways"

    id: int
    gateway_name: str
    sequence_number: int
    gateway_result: int
    status: str
    log_level: int

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    gateway_name = db.Column(db.String(255), unique=True, nullable=False)
    sequence_number = db.Column(db.Integer)
    gateway_result = db.Column(db.Integer)
    status = db.Column(db.String(255))
    log_level = db.Column(db.Integer)

    machines = db.relationship("Machine", secondary=MachineGatewayMapping.__tablename__, back_populates="gateways")
