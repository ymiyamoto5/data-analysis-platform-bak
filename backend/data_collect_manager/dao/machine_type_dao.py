from typing import List
from backend.data_collect_manager.models.db import db
from backend.data_collect_manager.models.machine_type import MachineType
from sqlalchemy.orm import joinedload, lazyload
from backend.common import common


class MachineTypeDAO:
    @staticmethod
    def select_all() -> List[MachineType]:
        machine_types: List[MachineType] = MachineType.query.all()

        return machine_types
