import traceback
from typing import List

from backend.app.api.deps import get_db
from backend.app.crud.crud_sensor_type import CRUDSensorType
from backend.app.schemas import sensor_type
from backend.common.common_logger import uvicorn_logger as logger
from backend.common.error_message import ErrorMessage, ErrorTypes
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=List[sensor_type.SensorType])
def fetch_sensor_types(db: Session = Depends(get_db)):
    try:
        sensor_types = CRUDSensorType.select_all(db)
        return sensor_types
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.READ_FAIL))
