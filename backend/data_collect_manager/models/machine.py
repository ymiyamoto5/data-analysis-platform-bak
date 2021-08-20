from dataclasses import dataclass
from backend.data_collect_manager.models.db import db
from backend.data_collect_manager.models.machine_type import MachineType
from backend.data_collect_manager.models.gateway import Gateway
from backend.data_collect_manager.models.machine_gateway_mapping import MachineGatewayMapping
from backend.data_collect_manager.models.data_collect_history import DataCollectHistory


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
    gateways: Gateway

    machine_id = db.Column(db.String(255), primary_key=True)
    machine_name = db.Column(db.String(255), unique=True, nullable=False)
    collect_status = db.Column(db.String(255))
    machine_type_id = db.Column(db.Integer, db.ForeignKey("machine_types.id"))

    # NOTE: MachineとGatewayはMany to Many
    gateways = db.relationship("Gateway", secondary=MachineGatewayMapping.__tablename__, back_populates="machines")

    # NOTE: MachineとMachineTypeはMany to One
    machine_type = db.relationship("MachineType", back_populates="machines")

    # NOTE: MachineとDataCollectHistoryはOne to Many
    data_collect_history = db.relationship("DataCollectHistory", back_populates="machine")
