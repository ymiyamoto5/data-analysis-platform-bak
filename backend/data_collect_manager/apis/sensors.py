from flask import Blueprint, jsonify

sensors = Blueprint("sensors", __name__)


@sensors.route("/sensors", methods=["GET"])
def fetch_sensors():
    """Sensorを起点に関連エンティティを全結合したデータを返す"""

    pass
