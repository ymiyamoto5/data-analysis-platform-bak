from pydantic import BaseModel, Field


class SensorTypeBase(BaseModel):
    sensor_type_name: str = Field(..., max_length=255)


class SensorType(SensorTypeBase):
    sensor_type_id: str = Field(..., max_length=255)

    class Config:
        orm_mode = True
