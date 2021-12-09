from backend.app.db.session import SessionLocal
from backend.app.services.data_recorder_service import DataRecorderService
from backend.app.worker.celery import celery_app
from celery import current_task
from sqlalchemy.orm.session import Session


@celery_app.task(acks_late=True)
def data_recorder_task(machine_id: str) -> str:
    # for i in range(1, 11):
    #     sleep(1)
    #     current_task.update_state(state="PROGRESS", meta={"process_percent": i * 10})
    # return f"test task return {machine_id}, {processed_dir_path}"

    current_task.update_state(state="PROGRESS", meta={"message": "data recording start"})

    db: Session = SessionLocal()

    DataRecorderService.record(db, machine_id)

    return f"task finished. {machine_id}"
