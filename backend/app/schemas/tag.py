from backend.common import common
from pydantic import BaseModel

# class TagBase(BaseModel):
#     collect_status: Optional[str]

#     @validator("collect_status")
#     def collect_status_validator(cls, v):
#         collect_statuses = (
#             common.COLLECT_STATUS.SETUP.value,
#             common.COLLECT_STATUS.START.value,
#             common.COLLECT_STATUS.PAUSE.value,
#             common.COLLECT_STATUS.STOP.value,
#             common.COLLECT_STATUS.RECORDED.value,
#         )
#         if v not in collect_statuses:
#             raise ValueError("Invalid status")
#         return v


class Tag(BaseModel):
    occurred_at: str
    tag: str
