from flask import Blueprint, jsonify, request
from marshmallow import Schema, fields, ValidationError, validate
import traceback
from backend.data_collect_manager.dao.gateway_dao import GatewayDAO
from backend.data_collect_manager.apis.api_common import character_validate
from backend.common.error_message import ErrorMessage, ErrorTypes
from backend.common import common
from backend.common.common_logger import logger


gateways = Blueprint("gateways", __name__)


class GatewaySchema(Schema):
    """POSTパラメータのvalidation用スキーマ"""

    gateway_id = fields.Str(required=True, validate=character_validate)
    sequence_number = fields.Int(validate=validate.Range(min=-1))
    gateway_result = fields.Int(validate=validate.Range(min=-1, max=1))
    status = fields.Str(validate=validate.OneOf((common.STATUS.STOP.value, common.STATUS.RUNNING.value)))
    log_level = fields.Int(validate=validate.Range(min=0, max=5))
    machine_id = fields.Str(validate=character_validate)


gateway_create_schema = GatewaySchema(only=("gateway_id", "log_level", "machine_id"))
gateway_update_schema = GatewaySchema(only=("sequence_number", "gateway_result", "status", "log_level", "machine_id"))


@gateways.route("/gateways", methods=["GET"])
def fetch_gateways():
    """Gatewayを起点に関連エンティティを全結合したデータを返す。"""

    gateways = GatewayDAO.select_all()

    return jsonify(gateways), 200


@gateways.route("/gateways/<string:gateway_id>", methods=["GET"])
def fetch_gateway(gateway_id):
    """指定Gatewayの情報を取得"""

    gateway = GatewayDAO.select_by_id(gateway_id)

    return jsonify(gateway), 200


@gateways.route("/gateways/<string:gateway_id>/machine", methods=["GET"])
def fetch_machine_id_from_gateway_id(gateway_id):
    """gateway_idをkeyにmachine_idを取得する。"""

    gateway = GatewayDAO.select_by_id(gateway_id)

    try:
        machine = gateway.machines[0].machine_id
    except Exception:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.NO_DATA)
        return jsonify({"message": message}), 400

    return jsonify(machine), 200


@gateways.route("/gateways", methods=["POST"])
def create():
    """Gatewayの作成"""

    json_data = request.get_json()

    if not json_data:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.NO_INPUT_DATA)
        return jsonify({"message": message}), 400

    try:
        data = gateway_create_schema.load(json_data)
    except ValidationError as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.VALID_ERROR, e.messages)
        return jsonify({"message": message}), 400

    try:
        GatewayDAO.insert(insert_data=data)
        return jsonify({}), 200
    except Exception as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.CREATE_FAIL, str(e))
        return jsonify({"message": message}), 500


@gateways.route("/gateways/<string:gateway_id>/update", methods=["POST"])
def update(gateway_id):
    """Gatewayの更新。更新対象のフィールドをパラメータとして受け取る。"""

    json_data = request.get_json()

    if not json_data:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.NO_INPUT_DATA)

    try:
        data = gateway_update_schema.load(json_data)
    except ValidationError as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.VALUE_ERROR, e.messages)
        return jsonify({"message": message}), 400

    try:
        GatewayDAO.update(gateway_id, update_data=data)
        return jsonify({}), 200
    except Exception as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.UPDATE_FAIL, str(e))
        return jsonify({"message": message}), 500


@gateways.route("/gateways/<string:gateway_id>/delete", methods=["POST"])
def delete(gateway_id):
    """Gatewayの削除"""

    try:
        GatewayDAO.delete(gateway_id)
        return jsonify({}), 200
    except Exception as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.DELETE_FAIL, str(e))
        return jsonify({"message": message}), 500
