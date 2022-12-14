from typing import List, Optional

from backend.app.schemas.sensor import Sensor
from backend.common import common
from pydantic import BaseModel, Field


class HandlerBase(BaseModel):
    pass


class Handler(HandlerBase):
    handler_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    handler_type: str = Field(..., max_length=255, regex="^[0-9a-zA-Z-_]+$")
    adc_serial_num: str = Field(..., max_length=255)
    sampling_frequency: int = Field(..., ge=1, le=100_000)
    sampling_ch_num: int = Field(..., ge=0, le=99)
    filewrite_time: int = Field(..., ge=1, le=360)
    gateway_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    sensors: List[Sensor]
    is_primary: bool
    is_cut_out_target: bool
    is_multi: bool

    class Config:
        orm_mode = True


class HandlerCreate(HandlerBase):
    handler_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    handler_type: str = Field(..., max_length=255, regex="^[0-9a-zA-Z-_]+$")
    adc_serial_num: str = Field(..., max_length=255)
    sampling_frequency: int = Field(..., ge=1, le=100_000)
    filewrite_time: int = Field(..., ge=1, le=360)
    gateway_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    is_primary: bool
    is_cut_out_target: bool
    is_multi: bool


class HandlerUpdate(HandlerBase):
    handler_type: Optional[str] = Field(max_length=255, regex="^[0-9a-zA-Z-_]+$")
    adc_serial_num: Optional[str] = Field(max_length=255)
    sampling_frequency: Optional[int] = Field(ge=1, le=100_000)
    filewrite_time: Optional[int] = Field(ge=1, le=360)
    is_primary: bool
    is_cut_out_target: bool
    is_multi: bool
