from backend.app.db.session import SessionLocal
from backend.app.services.cut_out_shot_service import CutOutShotService
from backend.app.worker.celery import celery_app
from celery import current_task
from sqlalchemy.orm.session import Session


@celery_app.task(acks_late=True)
def cut_out_shot_task(machine_id: str) -> str:
    current_task.update_state(state="PROGRESS", meta={"message": f"cut_out_shot start. machine_id: {machine_id}"})

    db: Session = SessionLocal()

    CutOutShotService.auto_cut_out_shot(db, machine_id)

    db.close()

    return f"cut_out_shot task finished. machine_id: {machine_id}"
