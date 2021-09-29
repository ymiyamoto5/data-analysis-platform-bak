from typing import List
from dataclasses import dataclass
from backend.data_collect_manager.models.handler import Handler
from backend.data_collect_manager.models.db import db


@dataclass
class Gateway(db.Model):
    __tablename__ = "gateways"

    gateway_id: str
    sequence_number: int
    gateway_result: int
    status: str
    log_level: int
    machine_id: str
    handlers: List[Handler]

    gateway_id = db.Column(db.String(255), primary_key=True)
    sequence_number = db.Column(db.Integer)
    gateway_result = db.Column(db.Integer)
    status = db.Column(db.String(255))
    log_level = db.Column(db.Integer)
    machine_id = db.Column(db.Integer, db.ForeignKey("machines.machine_id"), nullable=False)

    machine = db.relationship("Machine", back_populates="gateways")
    handlers = db.relationship("Handler", back_populates="gateway", cascade="all, delete")
