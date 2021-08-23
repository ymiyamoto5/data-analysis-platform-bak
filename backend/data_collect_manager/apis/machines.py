from flask import Blueprint, jsonify, request
from backend.data_collect_manager.dao.machine_dao import MachineDAO
from marshmallow import Schema, fields, ValidationError, validate
import traceback
from backend.data_collect_manager.apis.api_common import character_validate
from backend.common.common_logger import logger
from backend.common.error_message import ErrorMessage, ErrorTypes
from backend.common import common

machines = Blueprint("machines", __name__)


class MachineSchema(Schema):
    """POSTパラメータのvalidation用スキーマ"""

    machine_id = fields.Str(required=True, validate=character_validate)
    machine_name = fields.Str()
    collect_status = fields.Str(
        validate=validate.OneOf(
            (
                common.COLLECT_STATUS.SETUP.value,
                common.COLLECT_STATUS.START.value,
                common.COLLECT_STATUS.PAUSE.value,
                common.COLLECT_STATUS.STOP.value,
                common.COLLECT_STATUS.RECORDED.value,
            )
        )
    )
    machine_type_id = fields.Int()


machine_create_schema = MachineSchema(only=("machine_id", "machine_name", "machine_type_id"))
machine_update_schema = MachineSchema(only=("machine_name", "collect_status", "machine_type_id"))


@machines.route("/machines", methods=["GET"])
def fetch_machines():
    """Machineを起点に関連エンティティを全結合したデータを返す"""

    machines = MachineDAO.select_all()

    return jsonify(machines)


@machines.route("/machines/<string:machine_id>", methods=["GET"])
def fetch_machine(machine_id):
    """指定machineの情報を取得"""

    machine = MachineDAO.select_by_id(machine_id)

    return jsonify(machine)


@machines.route("/machines", methods=["POST"])
def create():
    """machineの作成"""

    json_data = request.get_json()

    if not json_data:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.NO_INPUT_DATA)
        return jsonify({"message": message}), 400

    try:
        data = machine_create_schema.load(json_data)
    except ValidationError as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.VALID_ERROR, e.messages)
        return jsonify({"message": message}), 400

    try:
        MachineDAO.insert(
            machine_id=data["machine_id"], machine_name=data["machine_name"], machine_type_id=data["machine_type_id"]
        )
        return jsonify({}), 200
    except Exception as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.CREATE_FAIL, str(e))
        return jsonify({"message": message}), 500


@machines.route("/machines/<string:machine_id>/update", methods=["POST"])
def update(machine_id):
    """machineの更新。更新対象のフィールドをパラメータとして受け取る。"""

    json_data = request.get_json()

    if not json_data:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.NO_INPUT_DATA)

    try:
        data = machine_update_schema.load(json_data)
    except ValidationError as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.VALUE_ERROR, e.messages)
        return jsonify({"message": message}), 400

    try:
        MachineDAO.update(machine_id, update_data=data)
        return jsonify({}), 200
    except Exception as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.UPDATE_FAIL, str(e))
        return jsonify({"message": message}), 500


@machines.route("/machines/<string:machine_id>/delete", methods=["POST"])
def delete(machine_id):
    """Machineの削除"""

    try:
        MachineDAO.delete(machine_id)
        return jsonify({}), 200
    except Exception as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.DELETE_FAIL, str(e))
        return jsonify({"message": message}), 500
