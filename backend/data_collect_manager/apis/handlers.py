from flask import Blueprint, jsonify, request
from backend.data_collect_manager.models.handler import Handler
from backend.data_collect_manager.models.db import db
from marshmallow import Schema, fields, ValidationError, validate
import traceback
import logging
from backend.data_collect_manager.apis.api_common import character_validate
from backend.common.error_message import ErrorMessage, ErrorTypes

# TODO: data_collect_managerのloggerを引き継ぐように設定したい。
logger = logging.getLogger(__name__)

handlers = Blueprint("handlers", __name__)


class HandlerSchema(Schema):
    """POSTパラメータのvalidation用スキーマ"""

    handler_id = fields.Str(required=True, validate=character_validate)
    adc_serial_num = fields.Str(validate=character_validate)
    handler_type = fields.Str()
    sampling_frequency = fields.Int(validate=validate.Range(min=1, max=100_000))
    sampling_ch_num = fields.Int(validate=validate.Range(min=1, max=16))
    filewrite_time = fields.Int(validate=validate.Range(min=1, max=60))


handler_create_schema = HandlerSchema()
handler_update_schema = HandlerSchema(
    only=("adc_serial_num", "handler_type", "sampling_frequency", "sampling_ch_num", "filewrite_time")
)


@handlers.route("/handlers", methods=["GET"])
def fetch_handlers():
    """handlerを起点に関連エンティティを全結合したデータを返す。"""

    handlers = Handler.query.all()

    return jsonify(handlers)


@handlers.route("/handlers/<string:handler_id>", methods=["GET"])
def fetch_handler(handler_id):
    """指定Handlerの情報を取得"""

    handler = Handler.query.get(handler_id)

    return jsonify(handler)


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

    handler_id: str = data["handler_id"]
    adc_serial_num: str = data["adc_serial_num"]
    handler_type: str = data["handler_type"]
    sampling_frequency: int = data["sampling_frequency"]
    sampling_ch_num: int = data["sampling_ch_num"]
    filewrite_time: int = data["filewrite_time"]

    new_handler = Handler(
        handler_id=handler_id,
        adc_serial_num=adc_serial_num,
        handler_type=handler_type,
        sampling_frequency=sampling_frequency,
        sampling_ch_num=sampling_ch_num,
        filewrite_time=filewrite_time,
    )

    try:
        db.session.add(new_handler)
        db.session.commit()
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

    handler = Handler.query.get(handler_id)

    if handler is None:
        message: str = ErrorMessage.generate_message(ErrorTypes.NOT_EXISTS, handler_id)
        logger.error(message)
        return jsonify({"message": message}), 404

    # 更新対象のプロパティをセット
    for key, value in data.items():
        setattr(handler, key, value)

    try:
        db.session.commit()
        return jsonify({}), 200
    except Exception as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.UPDATE_FAIL, str(e))
        return jsonify({"message": message}), 500


@handlers.route("/handlers/<string:handler_id>/delete", methods=["POST"])
def delete(handler_id):
    """Handlerの削除"""

    handler = Handler.query.get(handler_id)

    try:
        db.session.delete(handler)
        db.session.commit()
        return jsonify({}), 200
    except Exception as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.DELETE_FAIL, str(e))
        return jsonify({"message": message}), 500
