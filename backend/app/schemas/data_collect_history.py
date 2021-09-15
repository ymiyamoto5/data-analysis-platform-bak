from datetime import datetime
from pydantic import BaseModel, Field, Required


class DataCollectHistoryBase(BaseModel):
    machine_id: str = Field(..., max_length=255, regex="^[0-9a-zA-Z-]+$")
    machine_name: str = Field(..., max_length=255)
    started_at: datetime = Required
    ended_at: datetime


class DataCollectHistory(DataCollectHistoryBase):
    id: int

    class Config:
        orm_mode = True
