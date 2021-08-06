from dataclasses import dataclass
from backend.data_collect_manager.models.db import db
from backend.data_collect_manager.models.machine_type import MachineType
from backend.data_collect_manager.models.gateway import Gateway
from backend.data_collect_manager.models.machine_gateway_mapping import MachineGatewayMapping


@dataclass
class Machine(db.Model):
    __tablename__ = "machines"

    # NOTE: これらの定義は必須。無いとquery時にエラーになる。
    id: int
    machine_name: str
    machine_type_id: int
    # NOTE: MachineからMachineTypeを引くためのプロパティ
    machine_type: MachineType
    gateways: Gateway

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    machine_name = db.Column(db.String(255), unique=True, nullable=False)
    machine_type_id = db.Column(db.Integer, db.ForeignKey("machine_types.id"))

    # NOTE: MachineとGatewayはMany to Many
    gateways = db.relationship("Gateway", secondary=MachineGatewayMapping.__tablename__, back_populates="machines")
    # NOTE: MachineとMachineTypeはMany to One
    machine_type = db.relationship("MachineType", back_populates="machines")
