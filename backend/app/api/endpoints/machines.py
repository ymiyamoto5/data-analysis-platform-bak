from typing import List
from backend.app.crud.crud_machine import CRUDMachine
from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from backend.app.api.deps import get_db
from backend.app.schemas import machine


router = APIRouter()


@router.get("/", response_model=List[machine.Machine])
def fetch_machines(db: Session = Depends(get_db)):
    """Machineを起点に関連エンティティを全結合したデータを返す"""

    machines = CRUDMachine.select_all(db)
    return machines


@router.get("/{machine_id}", response_model=machine.Machine)
def fetch_machine(machine_id: str, db: Session = Depends(get_db)):
    """指定machineの情報を取得"""

    machine = CRUDMachine.select_by_id(db, machine_id)
    return machine


@router.post("/", response_model=machine.Machine)
def create(machine_in: machine.MachineCreate, db: Session = Depends(get_db)):
    """machineの作成"""

    machine = CRUDMachine.select_by_id(db, machine_id=machine_in.machine_id)
    if machine:
        raise HTTPException(status_code=400, detail="機器IDが重複しています")

    machine = CRUDMachine.insert(db, obj_in=machine_in)
    return machine


@router.put("/{machine_id}", response_model=machine.Machine)
def update(machine_id: str, machine_in: machine.MachineUpdate, db: Session = Depends(get_db)):
    """machineの更新。更新対象のフィールドをパラメータとして受け取る。"""

    machine = CRUDMachine.select_by_id(db, machine_id=machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="機器が存在しません")

    machine = CRUDMachine.update(db, db_obj=machine, obj_in=machine_in)
    return machine


@router.delete("/{machine_id}", response_model=machine.Machine)
def delete(machine_id: str, db: Session = Depends(get_db)):
    """machineの削除"""

    machine = CRUDMachine.select_by_id(db, machine_id=machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="機器が存在しません")

    machine = CRUDMachine.delete(db, db_obj=machine)
    return machine
