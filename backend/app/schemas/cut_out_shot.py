from pydantic import BaseModel, Field
from backend.common import common


class CutOutShotBase(BaseModel):
    machine_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    start_displacement: float = Field(None, ge=0.0, le=100.0)
    end_displacement: float = Field(None, ge=0.0, le=100.0)
    target_date_str: str = Field(...)
