from dataclasses import dataclass
from data_collect_manager.models.db import db
from data_collect_manager.models.gateway import Gateway
from data_collect_manager.models.machine_gateway_mapping import MachineGatewayMapping


@dataclass
class Machine(db.Model):
    __tablename__ = "machines"

    # NOTE: これらの定義は必須。無いとquery時にエラーになる。
    machine_id: str
    machine_type_id: int
    gateways: Gateway

    machine_id = db.Column(db.String(255), primary_key=True)
    machine_type_id = db.Column(db.Integer, db.ForeignKey("machine_types.id"))

    machine_type = db.relationship("MachineType")
    gateways = db.relationship("Gateway", secondary=MachineGatewayMapping.__tablename__, back_populates="machines")
