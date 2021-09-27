from typing import List
from backend.app.crud.crud_machine_type import CRUDMachineType
from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from backend.app.api.deps import get_db
from backend.app.schemas import machine_type
from backend.common.error_message import ErrorMessage, ErrorTypes
import traceback
from backend.common.common_logger import uvicorn_logger as logger


router = APIRouter()


@router.get("/", response_model=List[machine_type.MachineType])
def fetch_machine_types(db: Session = Depends(get_db)):
    """Machineを起点に関連エンティティを全結合したデータを返す"""

    try:
        machine_types = CRUDMachineType.select_all(db)
        return machine_types
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.READ_FAIL))
