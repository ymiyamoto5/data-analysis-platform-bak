from dataclasses import dataclass
from backend.data_collect_manager.models.db import db


@dataclass
class MachineGatewayMapping(db.Model):
    __tablename__ = "machine_gateway_mapping"

    machine_id: str
    gateway_id: str

    machine_id = db.Column(
        db.String, db.ForeignKey("machines.machine_id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True
    )
    gateway_id = db.Column(
        db.String, db.ForeignKey("gateways.gateway_id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True
    )
