from typing import Optional
from pydantic import BaseModel, Field
from backend.app.schemas.sensor_type import SensorType
from backend.common import common


class SensorBase(BaseModel):
    base_volt: Optional[float]
    base_load: Optional[float]
    initial_volt: Optional[float]


class Sensor(SensorBase):
    machine_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    sensor_name: str = Field(..., max_length=255)
    sensor_type_id: str = Field(..., max_length=255)
    sensor_id: str
    sensor_type: SensorType
    handler_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)

    class Config:
        orm_mode = True


class SensorCreate(SensorBase):
    sensor_name: str = Field(..., max_length=255)
    sensor_type_id: str = Field(..., max_length=255)
    handler_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)


class SensorUpdate(SensorBase):
    machine_id: Optional[str] = Field(..., max_length=255, regex=common.ID_PATTERN)
    sensor_name: Optional[str] = Field(..., max_length=255)
    sensor_type_id: Optional[str] = Field(..., max_length=255)
