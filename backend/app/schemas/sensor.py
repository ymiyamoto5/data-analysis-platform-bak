from typing import Optional
from pydantic import BaseModel, Field
from backend.app.schemas.sensor_type import SensorType
from backend.common import common


class SensorBase(BaseModel):
    machine_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    sensor_name: str = Field(..., max_length=255)
    sensor_type_id: str = Field(..., max_length=255)
    base_volt: Optional[float]
    base_load: Optional[float]
    initial_volt: Optional[float]
    handler_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)


class Sensor(SensorBase):
    sensor_id: str
    sensor_type: SensorType

    class Config:
        orm_mode = True
