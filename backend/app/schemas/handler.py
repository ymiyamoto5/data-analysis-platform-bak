from typing import List
from backend.app.schemas.sensor import Sensor
from pydantic import BaseModel, Field
from backend.common import common


class HandlerBase(BaseModel):
    handler_type: str = Field(max_length=255)
    adc_serial_num: str = Field(max_length=255)
    sampling_frequency: int
    sampling_ch_num: int
    filewrite_time: int
    gateway_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)


class Handler(HandlerBase):
    handler_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    sensors: List[Sensor]

    class Config:
        orm_mode = True
