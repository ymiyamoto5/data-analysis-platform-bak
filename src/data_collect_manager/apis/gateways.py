import json
from flask import Blueprint, jsonify, request, Response
from data_collect_manager.models.gateway import Gateway
from data_collect_manager.models.db import db

import logging

# TODO: data_collect_managerのloggerを引き継ぐように設定したい。
logger = logging.getLogger("data_collect_manager")

gateways = Blueprint("gateways", __name__)


@gateways.route("/gateways", methods=["GET"])
def get_gateways():
    """ Gatewayを起点に関連エンティティを全結合したデータを返す。"""

    gateways = Gateway.query.all()

    return jsonify(gateways)


@gateways.route("/gateway/<int:id>", methods=["GET"])
def get_gateway(id):
    """ 指定Gatewayの情報を取得 """

    gateway = Gateway.query.get(id)

    return jsonify(gateway)


@gateways.route("/gateway", methods=["POST"])
def create():
    """ Gatewayの作成 """

    pass


@gateways.route("/gateway/<int:id>/update_status", methods=["POST"])
def update_status(id):
    """ 指定Gatewayのstatus更新 """

    try:
        status: str = request.json["status"]
    except KeyError:
        message: str = "Invalid request key."
        return Response(response=json.dumps({"successful": False, "message": message}), status=400)

    if (status is None) or (status not in ("running", "stop")):
        message: str = f"The status '{status}' is invalid."
        logger.error(message)
        return Response(response=json.dumps({"successful": False, "message": message}), status=400)

    gateway = Gateway.query.get(id)

    if gateway is None:
        message: str = f"The gateway '{gateway}' is not found."
        logger.error(message)
        return Response(response=json.dumps({"successful": False, "message": message}), status=404)

    try:
        gateway.status = status
        db.session.commit()
        return Response(response=json.dumps({"successful": True}), status=200)
    except Exception as e:
        message: str = f"Update gateway {id} failed."
        logger.error(str(e))
        return Response(response=json.dumps({"successful": False, "message": message}), status=404)

