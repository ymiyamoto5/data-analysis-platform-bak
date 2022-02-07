import traceback

from backend.app.api.deps import get_db
from backend.app.crud.crud_celery_task import CRUDCeleryTask
from backend.app.models.celery_task import CeleryTask
from backend.common import common
from backend.common.common_logger import uvicorn_logger as logger
from backend.common.error_message import ErrorMessage, ErrorTypes
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/{task_id}")
def fetch_task_info(task_id: str):
    """指定タスクの情報を取得"""

    try:
        task = CRUDCeleryTask.select_by_id(task_id)
        return task
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.READ_FAIL))


@router.get("/{machine_id}/{task_type}/latest")
def fetch_latest_celery_task(
    machine_id: str = Path(..., max_length=255, regex=common.ID_PATTERN),
    task_type: str = Path(..., max_length=255),
    db: Session = Depends(get_db),
):
    """特定機器の指定した最新タスク情報を返す"""

    try:
        latest_task: CeleryTask = CRUDCeleryTask.select_latest_by_task_type(db=db, machine_id=machine_id, task_type=task_type)
        return latest_task
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.READ_FAIL))
