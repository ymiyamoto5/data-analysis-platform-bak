from pydantic import BaseModel, Field


class CeleryTaskBase(BaseModel):
    task_id: str = Field(..., max_length=255)
    data_collect_history_id: int
    task_type: str = Field(..., max_length=255)


class CeleryTask(CeleryTaskBase):
    pass


class CeleryTaskCreate(CeleryTaskBase):
    pass
