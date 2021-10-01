from typing import List
from backend.app.crud.crud_machine import CRUDMachine
from fastapi import Depends, APIRouter, HTTPException, Path
from sqlalchemy.orm import Session
from backend.app.api.deps import get_db
from backend.app.schemas import machine
from backend.common import common
from backend.common.error_message import ErrorMessage, ErrorTypes
import traceback
from backend.common.common_logger import uvicorn_logger as logger

router = APIRouter()


@router.get("/", response_model=List[machine.Machine])
def fetch_machines(db: Session = Depends(get_db)):
    """Machineを起点に関連エンティティを全結合したデータを返す"""

    try:
        machines = CRUDMachine.select_all(db)
        return machines
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.READ_FAIL))


@router.get("/{machine_id}", response_model=machine.Machine)
def fetch_machine(machine_id: str = Path(..., max_length=255, regex=common.ID_PATTERN), db: Session = Depends(get_db)):
    """指定machineの情報を取得"""

    try:
        machine = CRUDMachine.select_by_id(db, machine_id)
        return machine
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.READ_FAIL))


@router.post("/", response_model=machine.Machine)
def create(machine_in: machine.MachineCreate, db: Session = Depends(get_db)):
    """machineの作成"""

    machine = CRUDMachine.select_by_id(db, machine_id=machine_in.machine_id)
    if machine:
        raise HTTPException(status_code=400, detail="機器IDが重複しています")

    try:
        machine = CRUDMachine.insert(db, obj_in=machine_in)
        return machine
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.CREATE_FAIL))


@router.put("/{machine_id}", response_model=machine.Machine)
def update(
    machine_in: machine.MachineUpdate,
    machine_id: str = Path(..., max_length=255, regex=common.ID_PATTERN),
    db: Session = Depends(get_db),
):
    """machineの更新。更新対象のフィールドをパラメータとして受け取る。"""

    machine = CRUDMachine.select_by_id(db, machine_id=machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="機器が存在しません")

    try:
        machine = CRUDMachine.update(db, db_obj=machine, obj_in=machine_in)
        return machine
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.UPDATE_FAIL))


@router.delete("/{machine_id}", response_model=machine.Machine)
def delete(machine_id: str = Path(..., max_length=255, regex=common.ID_PATTERN), db: Session = Depends(get_db)):
    """machineの削除"""

    machine = CRUDMachine.select_by_id(db, machine_id=machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="機器が存在しません")

    try:
        machine = CRUDMachine.delete(db, db_obj=machine)
        return machine
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=ErrorMessage.generate_message(ErrorTypes.DELETE_FAIL))
