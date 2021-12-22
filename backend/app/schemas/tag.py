from typing import Optional

from pydantic import BaseModel, Field


class TagBase(BaseModel):
    occurred_at: str
    ended_at: Optional[str] = None
    tag: str = Field(..., max_length=255)


class Tag(TagBase):
    id: str
