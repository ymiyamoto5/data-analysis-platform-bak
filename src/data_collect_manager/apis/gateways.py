from flask import Blueprint, jsonify, request
from data_collect_manager.models.gateway import Gateway
from data_collect_manager.models.db import db
from marshmallow import Schema, fields, ValidationError, validate
import logging
import traceback
import os
import sys
from data_collect_manager.apis.api_common import character_validate

sys.path.append(os.path.join(os.path.dirname(__file__), "../../utils"))
from error_message import ErrorMessage, ErrorTypes  # type: ignore
import common

# TODO: data_collect_managerのloggerを引き継ぐように設定したい。
logger = logging.getLogger(__name__)

gateways = Blueprint("gateways", __name__)


class GatewaySchema(Schema):
    """ POSTパラメータのvalidation用スキーマ """

    gateway_id = fields.Str(required=True, validate=character_validate)
    sequence_number = fields.Int(validate=validate.Range(min=-1))
    gateway_result = fields.Int(validate=validate.Range(min=-1, max=1))
    status = fields.Str(validate=validate.OneOf((common.STATUS.STOP.value, common.STATUS.RUNNING.value)))
    log_level = fields.Int(validate=validate.Range(min=0, max=5))


gateway_create_schema = GatewaySchema(only=("gateway_id", "log_level"))
gateway_update_schema = GatewaySchema(only=("sequence_number", "gateway_result", "status", "log_level"))


@gateways.route("/gateways", methods=["GET"])
def fetch_gateways():
    """ Gatewayを起点に関連エンティティを全結合したデータを返す。"""

    gateways = Gateway.query.all()

    return jsonify(gateways)


@gateways.route("/gateways/<string:gateway_id>", methods=["GET"])
def fetch_gateway(gateway_id):
    """ 指定Gatewayの情報を取得 """

    gateway = Gateway.query.get(gateway_id)

    return jsonify(gateway)


@gateways.route("/gateways", methods=["POST"])
def create():
    """ Gatewayの作成 """

    json_data = request.get_json()

    if not json_data:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.NO_INPUT_DATA)

    try:
        data = gateway_create_schema.load(json_data)
    except ValidationError as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.VALID_ERROR, e.messages)
        return jsonify({"message": message}), 400

    gateway_id: str = data["gateway_id"]
    log_level: int = data["log_level"]

    new_gateway = Gateway(
        gateway_id=gateway_id,
        sequence_number=1,
        gateway_result=0,
        status=common.STATUS.STOP.value,
        log_level=log_level,
    )

    try:
        db.session.add(new_gateway)
        db.session.commit()
        return jsonify({}), 200
    except Exception as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.CREATE_FAIL, str(e))
        return jsonify({"message": message}), 500


@gateways.route("/gateways/<string:gateway_id>/update", methods=["POST"])
def update(gateway_id):
    """ Gatewayの更新。更新対象のフィールドをパラメータとして受け取る。 """

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

    gateway = Gateway.query.get(gateway_id)

    if gateway is None:
        message: str = ErrorMessage.generate_message(ErrorTypes.NOT_EXISTS, gateway_id)
        logger.error(message)
        return jsonify({"message": message}), 404

    # 更新対象のプロパティをセット
    for key, value in data.items():
        setattr(gateway, key, value)

    try:
        db.session.commit()
        return jsonify({}), 200
    except Exception as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.UPDATE_FAIL, str(e))
        return jsonify({"message": message}), 500


@gateways.route("/gateways/<string:gateway_id>/delete", methods=["POST"])
def delete(gateway_id):
    """ Gatewayの削除 """

    gateway = Gateway.query.get(gateway_id)

    try:
        db.session.delete(gateway)
        db.session.commit()
        return jsonify({}), 200
    except Exception as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.DELETE_FAIL, str(e))
        return jsonify({"message": message}), 500
