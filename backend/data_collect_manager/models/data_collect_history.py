from datetime import datetime
from typing import Optional
from dataclasses import dataclass
from backend.data_collect_manager.models.db import db
from backend.data_collect_manager.models.machine import Machine


@dataclass
class DataCollectHistory(db.Model):
    __tablename__ = "data_collect_history"

    id: int
    machine_id: str
    machine_name: str
    started_at: datetime
    ended_at: Optional[datetime]
    machine: Machine

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    machine_id = db.Column(db.String(255), db.ForeignKey("machines.machine_id"), nullable=False)
    machine_name = db.Column(db.String(255), nullable=False)
    started_at = db.Column(db.DateTime, nullable=False)
    ended_at = db.Column(db.DateTime)

    # Many To One
    machine = db.relationship("Machine", back_populates="data_collect_history")
