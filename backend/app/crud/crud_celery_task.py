from backend.app.models.celery_task import CeleryTask
from backend.app.schemas import celery_task
from celery.result import AsyncResult
from sqlalchemy.orm import Session


class CRUDCeleryTask:
    @staticmethod
    def select_by_id(task_id: str):
        task = AsyncResult(task_id)

        task_info = {
            "task_id": task.task_id,
            "status": task.status,
            "result": task.result,
            "traceback": task.traceback,
            "children": task.children,
            "date_done": task.date_done,
        }

        return task_info

    @staticmethod
    def insert(db: Session, obj_in: celery_task.CeleryTaskCreate) -> CeleryTask:
        new_data_celery_task = CeleryTask(
            task_id=obj_in.task_id,
            data_collect_history_id=obj_in.data_collect_history_id,
            task_type=obj_in.task_type,
        )

        db.add(new_data_celery_task)
        db.commit()
        return new_data_celery_task
