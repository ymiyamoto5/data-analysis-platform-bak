from backend.app.schemas import notification
from backend.common import common
from backend.common.common_logger import uvicorn_logger as logger
from fastapi import APIRouter

router = APIRouter()


@router.post("/", response_model=notification.Notification)
def create(notification_in: notification.NotificationCreate):
    """通知メッセージを登録"""

    severity: common.Severity = notification_in.severity

    if severity == common.Severity.INFO:
        logger.info(notification_in.message)
    if severity == common.Severity.WARN:
        logger.warn(notification_in.message)
    if severity == common.Severity.ERROR:
        logger.error(notification_in.message)
    if severity == common.Severity.CRITICAL:
        logger.critical(notification_in.message)

    return notification_in
