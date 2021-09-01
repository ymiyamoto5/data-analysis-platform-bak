from flask import Blueprint, jsonify, request
from backend.data_collect_manager.dao.handler_dao import HandlerDAO
from marshmallow import Schema, fields, ValidationError, validate
import traceback
from backend.data_collect_manager.apis.api_common import character_validate
from backend.common.error_message import ErrorMessage, ErrorTypes
from backend.common.common_logger import logger

handlers = Blueprint("handlers", __name__)


class HandlerSchema(Schema):
    """POSTパラメータのvalidation用スキーマ"""

    handler_id = fields.Str(required=True, validate=[character_validate, validate.Length(min=1, max=255)])
    adc_serial_num = fields.Str(validate=[character_validate, validate.Length(min=1, max=255)])
    handler_type = fields.Str(validate=validate.Length(min=1, max=255))
    sampling_frequency = fields.Int(validate=validate.Range(min=1, max=100_000))
    sampling_ch_num = fields.Int(validate=validate.Range(min=1, max=16))
    filewrite_time = fields.Int(validate=validate.Range(min=1, max=60))
    gateway_id = fields.Str(validate=[character_validate, validate.Length(min=1, max=255)])


handler_create_schema = HandlerSchema()
handler_update_schema = HandlerSchema(
    only=("adc_serial_num", "handler_type", "sampling_frequency", "sampling_ch_num", "filewrite_time", "gateway_id")
)


@handlers.route("/handlers", methods=["GET"])
def fetch_handlers():
    """handlerを起点に関連エンティティを全結合したデータを返す。"""

    handlers = HandlerDAO.select_all()

    return jsonify(handlers), 200


@handlers.route("/handlers/<string:handler_id>", methods=["GET"])
def fetch_handler(handler_id):
    """指定Handlerの情報を取得"""

    handler = HandlerDAO.select_by_id(handler_id)

    return jsonify(handler), 200


@handlers.route("/handlers", methods=["POST"])
def create():
    """Handlerの作成"""

    json_data = request.get_json()

    if not json_data:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.NO_INPUT_DATA)
        return jsonify({"message": message}), 400

    try:
        data = handler_create_schema.load(json_data)
    except ValidationError as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.VALID_ERROR, e.messages)
        return jsonify({"message": message}), 400

    try:
        HandlerDAO.insert(insert_data=data)
        return jsonify({}), 200
    except Exception as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.CREATE_FAIL, str(e))
        return jsonify({"message": message}), 500


@handlers.route("/handlers/<string:handler_id>/update", methods=["POST"])
def update(handler_id):
    """Handlerの更新。更新対象のフィールドをパラメータとして受け取る。"""

    json_data = request.get_json()

    if not json_data:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.NO_INPUT_DATA)

    try:
        data = handler_update_schema.load(json_data)
    except ValidationError as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.VALUE_ERROR, e.messages)
        return jsonify({"message": message}), 400

    try:
        HandlerDAO.update(handler_id, update_data=data)
        return jsonify({}), 200
    except Exception as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.UPDATE_FAIL, str(e))
        return jsonify({"message": message}), 500


@handlers.route("/handlers/<string:handler_id>/delete", methods=["POST"])
def delete(handler_id):
    """Handlerの削除"""

    try:
        HandlerDAO.delete(handler_id)
        return jsonify({}), 200
    except Exception as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.DELETE_FAIL, str(e))
        return jsonify({"message": message}), 500
