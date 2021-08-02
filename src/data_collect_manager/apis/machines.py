from flask import Blueprint
from data_collect_manager.models.machine import Machine

machines = Blueprint("machines", __name__)


@machines.route("/machines", methods=["GET"])
def get_machines():

    machines = Machine().query.all()
    return machines
