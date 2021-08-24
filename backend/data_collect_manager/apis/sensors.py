from flask import Blueprint, json, jsonify
from marshmallow import Schema, fields, ValidationError, validate
from backend.data_collect_manager.apis.api_common import character_validate
from backend.data_collect_manager.dao.sensor_dao import SensorDAO

sensors = Blueprint("sensors", __name__)


class SensorSchema(Schema):
    """POSTパラメータのvalidation用スキーマ"""

    sensor_id = fields.Str(required=True, validate=character_validate)
    sensor_name = fields.Str()
    sensor_type_id = fields.Int(required=True)
    handler_id = fields.Str(validate=character_validate)


sensor_create_schema = SensorSchema()
sensor_update_schema = SensorSchema(only=("sensor_name", "sensor_type_id", "handler_id"))


@sensors.route("/sensors", methods=["GET"])
def fetch_sensors():
    """Sensorを起点に関連エンティティを全結合したデータを返す"""

    sensor = SensorDAO.select_all()

    return jsonify(sensor), 200


@sensors.route("/sensors/<string:sensor_id>", methods=["GET"])
def fetch_sensor(sensor_id):
    """指定Sensorの情報を取得"""

    sensor = SensorDAO.select_by_id(sensor_id)

    return jsonify(sensor), 200
