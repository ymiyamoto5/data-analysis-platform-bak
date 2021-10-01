from pydantic import BaseModel, Field
from typing import Optional


class DataCollectHistoryDetailBase(BaseModel):
    data_collect_history_id: int
    sensor_id: str
    sensor_name: str = Field(..., max_length=255)
    sensor_type_id: str = Field(..., max_length=255)
    base_volt: Optional[float] = Field(None, ge=0.0, le=100.0)
    base_load: Optional[float] = Field(None, ge=0.0, le=100.0)
    initial_volt: Optional[float] = Field(None, ge=0.0, le=100.0)


class DataCollectHistoryDetail(DataCollectHistoryDetailBase):
    class Config:
        orm_mode = True


class DataCollectHistoryDetailUpdate(DataCollectHistoryDetailBase):
    pass
