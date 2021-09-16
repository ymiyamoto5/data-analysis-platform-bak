from datetime import datetime
from pydantic import BaseModel, Field
from backend.common import common
from typing import Optional


class DataCollectHistoryBase(BaseModel):
    ended_at: Optional[datetime]


class DataCollectHistory(DataCollectHistoryBase):
    id: int
    machine_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    machine_name: str = Field(..., max_length=255)
    started_at: datetime

    class Config:
        orm_mode = True
