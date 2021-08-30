from flask import Blueprint, jsonify, request
from marshmallow import Schema, fields, ValidationError
from backend.data_collect_manager.apis.api_common import character_validate
from backend.data_collect_manager.dao.sensor_dao import SensorDAO
from backend.common.error_message import ErrorMessage, ErrorTypes
import traceback
from backend.common.common_logger import logger

sensors = Blueprint("sensors", __name__)


class SensorSchema(Schema):
    """POSTパラメータのvalidation用スキーマ"""

    sensor_name = fields.Str()
    sensor_type_id = fields.Int(required=True)
    handler_id = fields.Str(validate=character_validate)


sensor_create_schema = SensorSchema()
sensor_update_schema = SensorSchema()


@sensors.route("/sensors", methods=["GET"])
def fetch_sensors():
    """Sensorを起点に関連エンティティを全結合したデータを返す"""

    sensor = SensorDAO.select_all()

    return jsonify(sensor), 200


@sensors.route("/sensors/<int:sensor_id>", methods=["GET"])
def fetch_sensor(sensor_id):
    """指定Sensorの情報を取得"""

    sensor = SensorDAO.select_by_id(sensor_id)

    return jsonify(sensor), 200


@sensors.route("/sensors", methods=["POST"])
def create():
    """Sensorの作成"""

    json_data = request.get_json()

    if not json_data:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.NO_INPUT_DATA)
        return jsonify({"message": message}), 400

    try:
        data = sensor_create_schema.load(json_data)
    except ValidationError as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.VALID_ERROR, e.messages)
        return jsonify({"message": message}), 400

    try:
        SensorDAO.insert(insert_data=data)
        return jsonify({}), 200
    except Exception as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.CREATE_FAIL, str(e))
        return jsonify({"message": message}), 500


@sensors.route("/sensors/<int:sensor_id>/update", methods=["POST"])
def update(sensor_id):
    """Sensorの更新。更新対象のフィールドをパラメータとして受け取る。"""

    json_data = request.get_json()

    if not json_data:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.NO_INPUT_DATA)

    try:
        data = sensor_update_schema.load(json_data)
    except ValidationError as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.VALUE_ERROR, e.messages)
        return jsonify({"message": message}), 400

    try:
        SensorDAO.update(sensor_id, update_data=data)
        return jsonify({}), 200
    except Exception as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.UPDATE_FAIL, str(e))
        return jsonify({"message": message}), 500


@sensors.route("/sensors/<int:sensor_id>/delete", methods=["POST"])
def delete(sensor_id):
    """Sensorの削除"""

    try:
        SensorDAO.delete(sensor_id)
        return jsonify({}), 200
    except Exception as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.DELETE_FAIL, str(e))
        return jsonify({"message": message}), 500
