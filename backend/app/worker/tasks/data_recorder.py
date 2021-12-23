from backend.app.db.session import SessionLocal
from backend.app.services.data_recorder_service import DataRecorderService
from backend.app.worker.celery import celery_app
from celery import current_task
from sqlalchemy.orm.session import Session


@celery_app.task(bind=True)
def data_recorder_task(self, machine_id: str) -> str:
    """データ記録処理をceleryタスクに登録する"""

    # print(f"Request: {self.request}")

    current_task.update_state(state="PROGRESS", meta={"message": f"data recording start. machine_id: {machine_id}"})

    db: Session = SessionLocal()

    DataRecorderService.record(db, machine_id)

    db.close()

    return f"data recording task finished. machine_id: {machine_id}"
