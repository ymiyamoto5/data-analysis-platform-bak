from flask import Blueprint, jsonify
from data_collect_manager.models.machine import Machine
from data_collect_manager.models.machine_type import MachineType
from data_collect_manager.models.db import db
import logging

# TODO: data_collect_managerのloggerを引き継ぐように設定したい。
logger = logging.getLogger("data_collect_manager")

machines = Blueprint("machines", __name__)


@machines.route("/machines", methods=["GET"])
def fetch_machines():
    """ Machineを起点に関連エンティティを全結合したデータを返す。
    """

    try:
        machines = Machine.query.all()
    except Exception as e:
        logger.error(str(e))

    return jsonify(machines)


@machines.route("/machines/<int:id>", methods=["GET"])
def fetch_gateway(id):
    """ 指定Gatewayの情報を取得 """

    machine = Machine.query.get(id)

    return jsonify(machine)
