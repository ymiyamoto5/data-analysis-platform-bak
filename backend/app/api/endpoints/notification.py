import traceback
from datetime import datetime
from typing import List

from backend.app.api.deps import get_db
from backend.app.crud.crud_data_collect_history import CRUDDataCollectHistory
from backend.app.crud.crud_gateway_event import CRUDGatewayEvent
from backend.app.crud.crud_machine import CRUDMachine
from backend.app.models.data_collect_history import DataCollectHistory
from backend.app.models.gateway_event import GatewayEvent
from backend.app.models.machine import Machine
from backend.app.schemas import notification
from backend.common import common
from backend.common.common_logger import uvicorn_logger as logger
from backend.common.error_message import ErrorMessage, ErrorTypes
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/", response_model=List[notification.Notification])
def fetch_gateway_events(db: Session = Depends(get_db)):
    """GWイベントの全記録を返す"""

    try:
        event: List[GatewayEvent] = CRUDGatewayEvent.select_all(db)
        return event
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.READ_FAIL))


@router.get("/{machine_id}/latest-error", response_model=notification.Notification)
def fetch_latest_gateway_error(machine_id: str = Path(..., max_length=255, regex=common.ID_PATTERN), db: Session = Depends(get_db)):
    """特定GWの最新のエラーを返す"""

    machine: Machine = CRUDMachine.select_by_id(db, machine_id)
    gateway_id_list: List[str] = []
    for gateway in machine.gateways:
        gateway_id_list.append(gateway.gateway_id)

    history: DataCollectHistory = CRUDDataCollectHistory.select_latest_by_machine_id(db, machine_id)
    started_at: datetime = history.started_at

    try:
        event: GatewayEvent = CRUDGatewayEvent.select_latest_error_by_gateway_ids(db, gateway_id_list, started_at)
        return event
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.READ_FAIL))


@router.post("/", response_model=notification.Notification)
def create(notification_in: notification.NotificationCreate, db: Session = Depends(get_db)):
    """通知メッセージを登録"""

    utc_now: datetime = datetime.utcnow()

    try:
        CRUDGatewayEvent.insert(db, obj_in=notification_in, utc_now=utc_now)
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.CREATE_FAIL))

    return
