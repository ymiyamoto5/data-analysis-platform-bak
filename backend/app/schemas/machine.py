from typing import List, Optional
from pydantic import BaseModel, Field, validator
from backend.common import common
from backend.app.schemas.gateway import Gateway
from backend.app.schemas.machine_type import MachineType


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
    # data_collect_history: List[DataCollectHistory] = []

    class Config:
        orm_mode = True


class MachineCreate(MachineBase):
    machine_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    machine_name: str = Field(..., max_length=255)
    machine_type_id: int


class MachineUpdate(MachineBase):
    machine_name: Optional[str] = Field(max_length=255)
    machine_type_id: Optional[int]
