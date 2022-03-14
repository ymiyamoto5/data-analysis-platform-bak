from backend.app.db.session import SessionLocal
from backend.app.worker.celery import celery_app
from backend.data_recorder.data_recorder import DataRecorder
from celery import current_task
from sqlalchemy.orm.session import Session


@celery_app.task(bind=True)
def data_recorder_task(self, machine_id: str, gateway_id: str, handler_id: str) -> str:
    """データ記録処理をceleryタスクに登録する"""

    current_task.update_state(state="PROGRESS", meta={"message": f"data recording start. {machine_id}_{gateway_id}_{handler_id}"})

    db: Session = SessionLocal()

    DataRecorder.record(db, machine_id, gateway_id, handler_id)

    db.close()

    return f"data recording task finished. {machine_id}_{gateway_id}_{handler_id}"
