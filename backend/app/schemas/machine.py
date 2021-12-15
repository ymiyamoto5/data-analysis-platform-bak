from typing import List, Optional

from backend.app.schemas.gateway import Gateway
from backend.app.schemas.machine_type import MachineType
from backend.common import common
from pydantic import BaseModel, Field, validator


class MachineBase(BaseModel):
    collect_status: Optional[str]

    @validator("collect_status")
    def collect_status_validator(cls, v):
        collect_statuses = (
            common.COLLECT_STATUS.SETUP.value,
            common.COLLECT_STATUS.START.value,
            common.COLLECT_STATUS.PAUSE.value,
            common.COLLECT_STATUS.STOP.value,
            common.COLLECT_STATUS.RECORDED.value,
        )
        if v not in collect_statuses:
            raise ValueError("Invalid status")
        return v


class Machine(MachineBase):
    machine_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    machine_name: str = Field(..., max_length=255)
    machine_type_id: int
    machine_type: MachineType
    gateways: List[Gateway] = []
    auto_cut_out_shot: bool
    start_displacement: Optional[float] = None
    end_displacement: Optional[float] = None
    margin: Optional[float] = None
    auto_predict: bool
    predict_model: Optional[str] = None
    model_version: Optional[str] = None
    start_point_dsl: Optional[str] = None
    max_point_dsl: Optional[str] = None
    break_point_dsl: Optional[str] = None

    class Config:
        orm_mode = True


class MachineCreate(MachineBase):
    machine_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    machine_name: str = Field(..., max_length=255)
    machine_type_id: int


class MachineUpdate(MachineBase):
    machine_name: Optional[str] = Field(max_length=255)
    machine_type_id: Optional[int]
    auto_cut_out_shot: Optional[bool]
    start_displacement: Optional[float]
    end_displacement: Optional[float]
    margin: Optional[float]
    auto_predict: Optional[bool]
    predict_model: Optional[str]
    model_version: Optional[str]
    start_point_dsl: Optional[str]
    max_point_dsl: Optional[str]
    break_point_dsl: Optional[str]
