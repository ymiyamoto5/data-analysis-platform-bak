from typing import Optional

from backend.common import common
from pydantic import BaseModel, Field


class TagBase(BaseModel):
    occurred_at: str
    ended_at: Optional[str] = None
    tag: str = Field(..., max_length=255)
    machine_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    experiment_id: str


class Tag(TagBase):
    id: str
