from datetime import datetime
from typing import List, Optional

from backend.app.schemas.data_collect_history_event import DataCollectHistoryEvent
from backend.app.schemas.data_collect_history_gateway import DataCollectHistoryGateway, DataCollectHistoryGatewayUpdate
from backend.app.schemas.data_collect_history_handler import DataCollectHistoryHandler, DataCollectHistoryHandlerUpdate
from backend.app.schemas.data_collect_history_sensor import DataCollectHistorySensor, DataCollectHistorySensorUpdate
from backend.common import common
from pydantic import BaseModel, Field


class DataCollectHistoryBase(BaseModel):
    ended_at: Optional[datetime]


class DataCollectHistory(DataCollectHistoryBase):
    id: int
    machine_id: str = Field(..., max_length=255, regex=common.ID_PATTERN)
    machine_name: str = Field(..., max_length=255)
    machine_type_id: int
    started_at: datetime
    data_collect_history_gateways: List[DataCollectHistoryGateway]
    data_collect_history_handlers: List[DataCollectHistoryHandler]
    data_collect_history_sensors: List[DataCollectHistorySensor]
    data_collect_history_events: List[DataCollectHistoryEvent]

    class Config:
        orm_mode = True


class DataCollectHistoryUpdate(DataCollectHistoryBase):
    data_collect_history_gateways: Optional[List[DataCollectHistoryGatewayUpdate]] = Field(None)
    data_collect_history_handlers: Optional[List[DataCollectHistoryHandlerUpdate]] = Field(None)
    data_collect_history_sensors: Optional[List[DataCollectHistorySensorUpdate]] = Field(None)
