from pydantic import BaseModel, Field


class GatewayBase(BaseModel):
    log_level: int


class Gateway(GatewayBase):
    gateway_id: str = Field(..., max_length=255, regex="^[0-9a-zA-Z-]+$")
    sequence_number: int
    gateway_result: int
    status: str
    machine_id: str

    class Config:
        orm_mode = True
