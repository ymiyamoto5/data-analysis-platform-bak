from typing import List
from dataclasses import dataclass
from backend.data_collect_manager.models.db import db
from backend.data_collect_manager.models.machine_type import MachineType
from backend.data_collect_manager.models.gateway import Gateway


@dataclass
class Machine(db.Model):
    __tablename__ = "machines"

    # NOTE: これらの定義は必須。無いとquery時にエラーになる。
    machine_id: str
    machine_name: str
    collect_status: str
    machine_type_id: int
    # NOTE: MachineからMachineTypeを引くためのプロパティ
    machine_type: MachineType
    gateways: List[Gateway]

    machine_id = db.Column(db.String(255), primary_key=True)
    machine_name = db.Column(db.String(255), nullable=False)
    collect_status = db.Column(db.String(255))
    machine_type_id = db.Column(db.Integer, db.ForeignKey("machine_types.id"), nullable=False)

    # NOTE: MachineとMachineTypeはMany to One
    machine_type = db.relationship("MachineType", back_populates="machines")
    # NOTE: MachineとGatewayはOne to Many
    gateways = db.relationship("Gateway", back_populates="machine", cascade="all, delete")
    # NOTE: MachineとDataCollectHistoryはOne to Many
    data_collect_history = db.relationship("DataCollectHistory", back_populates="machine")
