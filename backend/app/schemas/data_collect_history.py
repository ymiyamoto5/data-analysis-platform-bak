from datetime import datetime
from pydantic import BaseModel, Field
from backend.common import common
from typing import Optional, List
from backend.app.schemas.data_collect_history_detail import DataCollectHistoryDetail, DataCollectHistoryDetailUpdate


class DataCollectHistoryBase(BaseModel):
    ended_at: Optional[datetime]


class DataCollectHistory(DataCollectHistoryBase):
    id: int
    machine_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    machine_name: str = Field(..., max_length=255)
    machine_type_id: int
    started_at: datetime
    sampling_frequency: int
    sampling_ch_num: int
    data_collect_history_details: List[DataCollectHistoryDetail]

    class Config:
        orm_mode = True


class DataCollectHistoryUpdate(DataCollectHistoryBase):
    sampling_frequency: int
    data_collect_history_details: List[DataCollectHistoryDetailUpdate]
