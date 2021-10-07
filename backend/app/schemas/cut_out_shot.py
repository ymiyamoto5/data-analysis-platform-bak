from backend.common import common
from pydantic import BaseModel, Field


class CutOutShotBase(BaseModel):
    machine_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    target_date_str: str


class CutOutShotStrokeDisplacement(CutOutShotBase):
    start_stroke_displacement: float = Field(..., ge=0.0, le=100.0)
    end_stroke_displacement: float = Field(..., ge=0.0, le=100.0)


class CutOutShotPulse(CutOutShotBase):
    threshold: float
