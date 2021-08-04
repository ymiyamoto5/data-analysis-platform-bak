from dataclasses import dataclass
from data_collect_manager.models.db import db
from data_collect_manager.models.gateway import Gateway
from data_collect_manager.models.machine_gateway_mapping import MachineGatewayMapping


@dataclass
class Machine(db.Model):
    __tablename__ = "machines"

    # NOTE: これらの定義は必須。無いとquery時にエラーになる。
    id: int
    machine_name: str
    machine_type_id: int
    gateways: Gateway

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    machine_name = db.Column(db.String(255), unique=True, nullable=False)
    machine_type_id = db.Column(db.Integer, db.ForeignKey("machine_types.id"))

    machine_type = db.relationship("MachineType")
    gateways = db.relationship("Gateway", secondary=MachineGatewayMapping.__tablename__, back_populates="machines")
