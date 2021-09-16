from typing import List
from backend.app.crud.crud_machine import CRUDMachine
from backend.common.common_logger import logger
from backend.common.error_message import ErrorMessage, ErrorTypes
from backend.common import common
import traceback
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

    machine = CRUDMachine.insert(db, insert_data=machine_in)
    return machine


# @router.route("/machines/<string:machine_id>/update", methods=["POST"])
# def update(machine_id):
#     """machineの更新。更新対象のフィールドをパラメータとして受け取る。"""

#     json_data = request.get_json()

#     if not json_data:
#         logger.error(traceback.format_exc())
#         message: str = ErrorMessage.generate_message(ErrorTypes.NO_INPUT_DATA)

#     try:
#         data = machine_update_schema.load(json_data)
#     except ValidationError as e:
#         logger.error(traceback.format_exc())
#         message: str = ErrorMessage.generate_message(ErrorTypes.VALUE_ERROR, e.messages)
#         return jsonify({"message": message}), 400

#     try:
#         MachineDAO.update(machine_id, update_data=data)
#         return jsonify({}), 200
#     except Exception as e:
#         logger.error(traceback.format_exc())
#         message: str = ErrorMessage.generate_message(ErrorTypes.UPDATE_FAIL, str(e))
#         return jsonify({"message": message}), 500


# @router.route("/machines/<string:machine_id>/delete", methods=["POST"])
# def delete(machine_id):
#     """Machineの削除"""

#     try:
#         MachineDAO.delete(machine_id)
#         return jsonify({}), 200
#     except Exception as e:
#         logger.error(traceback.format_exc())
#         message: str = ErrorMessage.generate_message(ErrorTypes.DELETE_FAIL, str(e))
#         return jsonify({"message": message}), 500
