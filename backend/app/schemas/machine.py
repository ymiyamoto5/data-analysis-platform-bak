from typing import List
from pydantic import BaseModel, Field, validator
from backend.common import common
from backend.app.schemas.gateway import Gateway
from backend.app.schemas.machine_type import MachineType


class MachineBase(BaseModel):
    machine_name: str = Field(..., max_length=255)
    collect_status: str
    machine_type_id: int

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
    machine_id: str = Field(..., max_length=255, regex="^[0-9a-zA-Z-]+$")
    machine_type: MachineType
    gateways: List[Gateway] = []
    # data_collect_history: List[DataCollectHistory] = []

    class Config:
        orm_mode = True


class MachineCreate(MachineBase):
    machine_id: str = Field(..., max_length=255, regex="^[0-9a-zA-Z-]+$")
