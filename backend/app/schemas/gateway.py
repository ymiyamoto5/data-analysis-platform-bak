from typing import List
from backend.app.schemas.handler import Handler
from pydantic import BaseModel, Field


class GatewayBase(BaseModel):
    pass


class Gateway(GatewayBase):
    gateway_id: str = Field(..., max_length=255, regex="^[0-9a-zA-Z-]+$")
    sequence_number: int
    gateway_result: int
    status: str
    log_level: int
    machine_id: str
    handlers: List[Handler]

    class Config:
        orm_mode = True
