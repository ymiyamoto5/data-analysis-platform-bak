from typing import List, Optional
from backend.app.schemas.sensor import Sensor
from pydantic import BaseModel, Field
from backend.common import common


class HandlerBase(BaseModel):
    pass


class Handler(HandlerBase):
    handler_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    handler_type: str = Field(max_length=255)
    adc_serial_num: str = Field(max_length=255)
    sampling_frequency: int
    sampling_ch_num: int
    filewrite_time: int
    gateway_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    sensors: List[Sensor]

    class Config:
        orm_mode = True


class HandlerCreate(HandlerBase):
    handler_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    handler_type: str = Field(max_length=255)
    adc_serial_num: str = Field(max_length=255)
    sampling_frequency: int
    sampling_ch_num: int
    filewrite_time: int
    gateway_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)


class HandlerUpdate(HandlerBase):
    handler_type: Optional[str] = Field(max_length=255)
    adc_serial_num: Optional[str] = Field(max_length=255)
    sampling_frequency: Optional[int]
    sampling_ch_num: Optional[int]
    filewrite_time: Optional[int]
