from backend.app.db.session import SessionLocal
from backend.app.services.data_recorder_service import DataRecorderService
from backend.app.worker.celery import celery_app
from celery import current_task
from sqlalchemy.orm.session import Session


@celery_app.task(acks_late=True)
def data_recorder_task(machine_id: str) -> str:
    """データ記録処理をceleryタスクに登録する"""

    current_task.update_state(state="PROGRESS", meta={"message": "data recording start"})

    db: Session = SessionLocal()

    DataRecorderService.record(db, machine_id)

    db.close()

    return f"data recording task finished. {machine_id}"
