from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DataCollectHistoryEventBase(BaseModel):
    ended_at: Optional[datetime]


class DataCollectHistoryEvent(DataCollectHistoryEventBase):
    data_collect_history_id: int
    event_id: int
    event_name: str = Field(..., max_length=255)
    occurred_at: datetime

    class Config:
        orm_mode = True


class DataCollectHistoryEventUpdate(DataCollectHistoryEventBase):
    pass
