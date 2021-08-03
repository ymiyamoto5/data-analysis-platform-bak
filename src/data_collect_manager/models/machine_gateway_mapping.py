from dataclasses import dataclass
from data_collect_manager.models.db import db


@dataclass
class MachineGatewayMapping(db.Model):
    __tablename__ = "machine_gateway_mapping"

    machine_id: int
    gateway_id: int

    machine_id = db.Column(db.Integer, db.ForeignKey("machines.id"), primary_key=True)
    gateway_id = db.Column(db.Integer, db.ForeignKey("gateways.id"), primary_key=True)
