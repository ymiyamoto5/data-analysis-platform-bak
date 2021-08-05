from flask import Blueprint, jsonify
from data_collect_manager.models.machine import Machine
from data_collect_manager.models.db import db
import logging


# TODO: data_collect_managerのloggerを引き継ぐように設定したい。
logger = logging.getLogger(__name__)

machines = Blueprint("machines", __name__)


@machines.route("/machines", methods=["GET"])
def fetch_machines():
    """ Machineを起点に関連エンティティを全結合したデータを返す """

    machines = Machine.query.all()

    return jsonify(machines)


@machines.route("/machines/<int:id>", methods=["GET"])
def fetch_gateway(id):
    """ 指定Gatewayの情報を取得 """

    machine = Machine.query.get(id)

    return jsonify(machine)
