from typing import Optional

from backend.app.schemas.sensor_type import SensorType
from backend.common import common
from pydantic import BaseModel, Field


class SensorBase(BaseModel):
    pass


class Sensor(SensorBase):
    machine_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    sensor_name: str = Field(..., max_length=255)
    sensor_type_id: str = Field(..., max_length=255)
    sensor_id: str
    sensor_type: SensorType
    handler_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    slope: float
    intercept: float

    class Config:
        orm_mode = True


class SensorCreate(SensorBase):
    sensor_name: str = Field(..., max_length=255)
    sensor_type_id: str = Field(..., max_length=255)
    handler_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    slope: float
    intercept: float
    start_point_dsl: Optional[str] = None
    max_point_dsl: Optional[str] = None
    break_point_dsl: Optional[str] = None


class SensorUpdate(SensorBase):
    machine_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    sensor_name: Optional[str] = Field(..., max_length=255)
    sensor_type_id: Optional[str] = Field(..., max_length=255)
    slope: Optional[float] = None
    intercept: Optional[float] = None
    start_point_dsl: Optional[str]
    max_point_dsl: Optional[str]
    break_point_dsl: Optional[str]


class SensorDelete(SensorBase):
    machine_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
