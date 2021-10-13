from typing import List, Optional

from backend.app.schemas.handler import Handler
from backend.common import common
from pydantic import BaseModel, Field


class GatewayBase(BaseModel):
    pass


class Gateway(GatewayBase):
    gateway_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    sequence_number: int
    gateway_result: int
    status: str
    log_level: int = Field(..., ge=1, le=5)
    machine_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    handlers: List[Handler]

    class Config:
        orm_mode = True


class GatewayCreate(GatewayBase):
    gateway_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    log_level: int = Field(..., ge=1, le=5)
    machine_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)


class GatewayUpdate(GatewayBase):
    log_level: int = Field(..., ge=1, le=5)


class GatewayUpdateFromGateway(GatewayBase):
    sequence_number: Optional[int] = None
    gateway_result: Optional[int] = None
    status: Optional[str] = None
    log_level: Optional[int] = Field(None, ge=1, le=5)
