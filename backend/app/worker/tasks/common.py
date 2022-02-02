from backend.app.crud.crud_machine import CRUDMachine
from backend.app.db.session import SessionLocal
from backend.app.models.machine import Machine
from sqlalchemy.orm.session import Session


def get_collect_status(machine_id) -> str:
    """データ収集ステータスを取得する"""

    # NOTE: DBセッションを使いまわすと更新データが得られないため、新しいセッション作成
    db: Session = SessionLocal()
    machine: Machine = CRUDMachine.select_by_id(db, machine_id)
    collect_status: str = machine.collect_status
    db.close()

    return collect_status
