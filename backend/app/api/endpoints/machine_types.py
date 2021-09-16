from typing import List
from backend.app.crud.crud_machine_type import CRUDMachineType
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from backend.app.api.deps import get_db
from backend.app.schemas import machine_type


router = APIRouter()


@router.get("/", response_model=List[machine_type.MachineType])
def fetch_machine_types(db: Session = Depends(get_db)):
    """Machineを起点に関連エンティティを全結合したデータを返す"""

    machines = CRUDMachineType.select_all(db)
    return machines
