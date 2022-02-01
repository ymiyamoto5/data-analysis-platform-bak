from backend.app.models.celery_task import CeleryTask
from backend.app.models.data_collect_history import DataCollectHistory
from backend.app.schemas import celery_task
from celery.result import AsyncResult
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload


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
    def select_latest_by_task_type(db: Session, machine_id: str, task_type: str) -> CeleryTask:
        celery_task: CeleryTask = (
            db.query(CeleryTask)
            .filter_by(task_type=task_type)
            .order_by(desc(CeleryTask.data_collect_history_id))
            .options(
                joinedload(CeleryTask.data_collect_history),
            )
            .filter(DataCollectHistory.machine_id == machine_id)
            .first()
        )

        return celery_task

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
