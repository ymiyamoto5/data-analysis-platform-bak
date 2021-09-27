from pydantic import BaseModel, Field
from typing import Optional


class DataCollectHistoryDetailBase(BaseModel):
    pass


class DataCollectHistoryDetail(DataCollectHistoryDetailBase):
    data_collect_history_id: int
    sensor_id: str
    sensor_name: str = Field(..., max_length=255)
    sensor_type_id: str = Field(..., max_length=255)
    base_volt: Optional[float] = None
    base_load: Optional[float] = None
    initial_volt: Optional[float] = None

    class Config:
        orm_mode = True


class DataCollectHistoryDetailUpdate(DataCollectHistoryDetailBase):
    data_collect_history_id: int
    sensor_id: str
    sensor_name: str = Field(..., max_length=255)
    sensor_type_id: str = Field(..., max_length=255)
    base_volt: Optional[float] = None
    base_load: Optional[float] = None
    initial_volt: Optional[float] = None
