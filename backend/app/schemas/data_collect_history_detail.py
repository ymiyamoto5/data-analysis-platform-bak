from typing import Optional

from pydantic import BaseModel, Field


class DataCollectHistoryDetailBase(BaseModel):
    data_collect_history_id: int
    sensor_id: str
    sensor_name: str = Field(..., max_length=255)
    sensor_type_id: str = Field(..., max_length=255)
    slope: float
    intercept: float
    start_point_dsl: Optional[str] = None
    max_point_dsl: Optional[str] = None
    break_point_dsl: Optional[str] = None


class DataCollectHistoryDetail(DataCollectHistoryDetailBase):
    class Config:
        orm_mode = True


class DataCollectHistoryDetailUpdate(DataCollectHistoryDetailBase):
    pass
