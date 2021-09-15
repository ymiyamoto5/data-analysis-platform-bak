from pydantic import BaseModel, Field


class MachineTypeBase(BaseModel):
    machine_type_name: str = Field(..., max_length=255)


class MachineType(MachineTypeBase):
    machine_type_id: int

    class Config:
        orm_mode = True
