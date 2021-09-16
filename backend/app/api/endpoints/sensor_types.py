from typing import List
from backend.app.crud.crud_sensor_type import CRUDSensorType
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from backend.app.api.deps import get_db
from backend.app.schemas import sensor_type


router = APIRouter()


@router.get("/", response_model=List[sensor_type.SensorType])
def fetch_sensor_types(db: Session = Depends(get_db)):
    sensors = CRUDSensorType.select_all(db)
    return sensors
