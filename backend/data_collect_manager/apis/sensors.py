from flask import Blueprint, jsonify
from backend.data_collect_manager.models.sensor import Sensor
from backend.common.common_logger import logger

sensors = Blueprint("sensors", __name__)


@sensors.route("/sensors", methods=["GET"])
def fetch_sensors():
    """Sensorを起点に関連エンティティを全結合したデータを返す"""

    sensors = Sensor.query.all()

    return jsonify(sensors)


@sensors.route("/sensors/<int:id>", methods=["GET"])
def fetch_sensor(id):
    """指定Sensorの情報を取得"""

    sensor = Sensor.query.get(id)

    return jsonify(sensor)
