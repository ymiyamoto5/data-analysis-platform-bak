from typing import List, Optional

from backend.app.schemas.data_collect_history_handler import DataCollectHistoryHandler
from backend.common import common
from pydantic import BaseModel, Field


class DataCollectHistoryGatewayBase(BaseModel):
    data_collect_history_id: int


class DataCollectHistoryGateway(DataCollectHistoryGatewayBase):
    gateway_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    log_level: int = Field(..., ge=1, le=5)
    data_collect_history_handlers: List[DataCollectHistoryHandler]

    class Config:
        orm_mode = True


class DataCollectHistoryGatewayCreate(DataCollectHistoryGatewayBase):
    gateway_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    log_level: int = Field(..., ge=1, le=5)


class DataCollectHistoryGatewayUpdate(DataCollectHistoryGatewayBase):
    log_level: int = Field(..., ge=1, le=5)


class DataCollectHistoryGatewayUpdateFromDataCollectHistoryGateway(DataCollectHistoryGatewayBase):
    log_level: Optional[int] = Field(None, ge=1, le=5)
