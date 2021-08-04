from flask import Blueprint, jsonify
from data_collect_manager.models.machine import Machine
from data_collect_manager.models.machine_type import MachineType
from data_collect_manager.models.db import db

machines = Blueprint("machines", __name__)


@machines.route("/machines", methods=["GET"])
def fetch_machines():
    """ MachineTypeを起点に関連エンティティを全結合したデータを返す。
        NOTE: machine_type_nameも含めるため、最上位エンティティであるMachineTypeから引いている。
    """

    machines = MachineType.query.all()

    return jsonify(machines)


@machines.route("/machines/<int:id>", methods=["GET"])
def fetch_gateway(id):
    """ 指定Gatewayの情報を取得 """

    machine = Machine.query.get(id)

    return jsonify(machine)
