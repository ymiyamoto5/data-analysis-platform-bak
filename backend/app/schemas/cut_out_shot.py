from backend.common import common
from pydantic import BaseModel, Field


class CutOutShotBase(BaseModel):
    machine_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)


class CutOutShotStrokeDisplacement(CutOutShotBase):
    target_date_str: str
    start_stroke_displacement: float = Field(..., ge=0.0, le=100.0)
    end_stroke_displacement: float = Field(..., ge=0.0, le=100.0)
    margin: float = Field(..., ge=0.0, le=10000.0)


class CutOutShotPulse(CutOutShotBase):
    target_date_str: str
    threshold: float = Field(..., ge=-100.0, le=100.0)


class CutOutShotCancel(CutOutShotBase):
    pass
