from typing import Optional

from backend.common import common
from pydantic import BaseModel, Field


class DataCollectHistorySensorBase(BaseModel):
    data_collect_history_id: int
    sensor_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    handler_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    gateway_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    sensor_name: str = Field(..., max_length=255)
    sensor_type_id: str = Field(..., max_length=255)
    slope: float
    intercept: float
    start_point_dsl: Optional[str] = None
    max_point_dsl: Optional[str] = None
    break_point_dsl: Optional[str] = None


class DataCollectHistorySensor(DataCollectHistorySensorBase):
    class Config:
        orm_mode = True


class DataCollectHistorySensorUpdate(DataCollectHistorySensorBase):
    pass
