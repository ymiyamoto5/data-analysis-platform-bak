from typing import List
from backend.app.crud.crud_machine import CRUDMachine
from backend.data_collect_manager.apis.api_common import character_validate
from backend.common.common_logger import logger
from backend.common.error_message import ErrorMessage, ErrorTypes
from backend.common import common
import traceback
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from backend.app.api.deps import get_db
from backend.app.schemas import machine


router = APIRouter()


@router.get("/", response_model=List[machine.Machine])
def fetch_machines(db: Session = Depends(get_db)):
    """Machineを起点に関連エンティティを全結合したデータを返す"""

    try:
        machines = CRUDMachine.select_all(db)
        return machines
    except Exception as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.READ_FAIL, str(e))
        return {"message": message}


@router.get("/{machine_id}", response_model=machine.Machine)
def fetch_machine(machine_id: str, db: Session = Depends(get_db)):
    """指定machineの情報を取得"""

    try:
        machine = CRUDMachine.select_by_id(db, machine_id)
        return machine
    except Exception as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.READ_FAIL, str(e))
        return {"message": message}


# @router.route("/machines", methods=["POST"])
# def create():
#     """machineの作成"""

#     json_data = request.get_json()

#     if not json_data:
#         logger.error(traceback.format_exc())
#         message: str = ErrorMessage.generate_message(ErrorTypes.NO_INPUT_DATA)
#         return jsonify({"message": message}), 400

#     try:
#         data = machine_create_schema.load(json_data)
#     except ValidationError as e:
#         logger.error(traceback.format_exc())
#         message: str = ErrorMessage.generate_message(ErrorTypes.VALID_ERROR, e.messages)
#         return jsonify({"message": message}), 400

#     try:
#         MachineDAO.insert(insert_data=data)
#         return jsonify({}), 200
#     except Exception as e:
#         logger.error(traceback.format_exc())
#         # HACK: Exception文字列の中身からエラー内容を判定して詳細メッセージを設定
#         detail_message: Optional[str] = None
#         if "UNIQUE constraint failed" in str(e):
#             detail_message = "IDは重複不可です"
#         message: str = ErrorMessage.generate_message(ErrorTypes.CREATE_FAIL, detail_message)
#         return jsonify({"message": message}), 500


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
