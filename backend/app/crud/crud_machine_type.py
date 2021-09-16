from typing import List
from backend.app.models.machine_type import MachineType
from sqlalchemy.orm import Session


class CRUDMachineType:
    @staticmethod
    def select_all(db: Session) -> List[MachineType]:
        machine_types: List[MachineType] = db.query(MachineType).all()

        return machine_types
