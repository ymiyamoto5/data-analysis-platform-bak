from datetime import datetime

from backend.common import common
from pydantic import BaseModel, Field


class NotificationBase(BaseModel):
    gateway_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    # severity: common.Severity = Field(...)
    severity: str = Field(...)
    message: str = Field(..., max_length=8096)


class Notification(NotificationBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True


class NotificationCreate(NotificationBase):
    pass
