from dataclasses import dataclass
from data_collect_manager.models.db import db


@dataclass
class MachineType(db.Model):
    __tablename__ = "machine_types"

    # NOTE: dataclassにして型定義をしておくと簡単にjsonシリアライズできる。
    # https://stackoverflow.com/questions/5022066/how-to-serialize-sqlalchemy-result-to-json
    id: int
    machine_type_name: str

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    machine_type_name = db.Column(db.String(255), unique=True, nullable=False)

    machines = db.relationship("Machine", back_populates="machine_type")
