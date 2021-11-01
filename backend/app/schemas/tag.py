from pydantic import BaseModel, Field


class TagBase(BaseModel):
    occurred_at: str
    tag: str = Field(..., max_length=255)


class Tag(TagBase):
    id: str
