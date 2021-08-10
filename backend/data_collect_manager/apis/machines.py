from flask import Blueprint, jsonify
from backend.data_collect_manager.models.machine import Machine
from backend.common.common_logger import logger

machines = Blueprint("machines", __name__)


@machines.route("/machines", methods=["GET"])
def fetch_machines():
    """Machineを起点に関連エンティティを全結合したデータを返す"""

    machines = Machine.query.all()

    return jsonify(machines)


@machines.route("/machines/<int:id>", methods=["GET"])
def fetch_gateway(id):
    """指定Gatewayの情報を取得"""

    machine = Machine.query.get(id)

    return jsonify(machine)
