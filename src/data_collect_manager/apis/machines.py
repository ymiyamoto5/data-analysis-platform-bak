from flask import Blueprint, jsonify
from data_collect_manager.models.machine import Machine
from data_collect_manager.models.machine_type import MachineType
from data_collect_manager.models.db import db

machines = Blueprint("machines", __name__)


@machines.route("/machines", methods=["GET"])
def get_machines():
    """ MachineTypeを起点に関連エンティティを全結合したデータを返す。"""

    # machines = db.session.query(Machine).join(MachineType)
    machines = MachineType.query.all()

    return jsonify(machines)
