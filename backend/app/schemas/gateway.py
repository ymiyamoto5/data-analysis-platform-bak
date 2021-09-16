from typing import List, Optional
from backend.app.schemas.handler import Handler
from pydantic import BaseModel, Field
from backend.common import common


class GatewayBase(BaseModel):
    pass


class Gateway(GatewayBase):
    gateway_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    sequence_number: int
    gateway_result: int
    status: str
    log_level: int
    machine_id: str
    handlers: List[Handler]

    class Config:
        orm_mode = True


class GatewayUpdate(GatewayBase):
    sequence_number: Optional[int]
    gateway_result: Optional[int]
    status: Optional[str]
    log_level: Optional[int]
    machine_id: Optional[str]
