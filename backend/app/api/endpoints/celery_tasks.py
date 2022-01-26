import traceback

from backend.app.crud.crud_celery_task import CRUDCeleryTask
from backend.common.common_logger import uvicorn_logger as logger
from backend.common.error_message import ErrorMessage, ErrorTypes
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/{task_id}")
def fetch_task_info(task_id: str):
    """指定タスクの情報を取得"""

    try:
        celery_task = CRUDCeleryTask.select_by_id(task_id)
        return celery_task
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.READ_FAIL))
