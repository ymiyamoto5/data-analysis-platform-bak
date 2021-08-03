from dataclasses import dataclass
from data_collect_manager.models.db import db


@dataclass
class Machine(db.Model):
    __tablename__ = "machines"

    id: int
    machine_name: str
    machine_type_id: int

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    machine_name = db.Column(db.String(255), unique=True, nullable=False)
    machine_type_id = db.Column(db.Integer, db.ForeignKey("machine_types.id"))

    machine_type = db.relationship("MachineType")
