from flask import Blueprint, jsonify, request
from data_collect_manager.models.gateway import Gateway
from data_collect_manager.models.db import db

import logging

# TODO: data_collect_managerのloggerを引き継ぐように設定したい。
logger = logging.getLogger("data_collect_manager")

gateways = Blueprint("gateways", __name__)


@gateways.route("/gateway", methods=["GET"])
def get_gateways():
    """ Gatewayを起点に関連エンティティを全結合したデータを返す。"""

    gateways = Gateway.query.all()

    return jsonify(gateways)


@gateways.route("/gateway/<string:gateway_id>", methods=["GET"])
def get_gateway(gateway_id):
    """ 指定Gatewayの情報を取得 """

    gateway = Gateway.query.get(gateway_id)

    return jsonify(gateway)


# @gateways.route("/gateway/<string:gateway_name>", methods=["GET"])
# def get_gateway_by_name(gateway_name):
#     """ 指定Gatewayの情報をGateway名から取得 """

#     gateway = Gateway.query.filter_by(gateway_name=gateway_name).first()

#     if gateway is None:
#         message: str = f"The gateway '{gateway_name}' is not found."
#         logger.error(message)
#         return jsonify({"error": message}), 404

#     return jsonify(gateway)


@gateways.route("/gateway", methods=["POST"])
def create():
    """ Gatewayの作成 """

    pass


@gateways.route("/gateway/<string:gateway_id>/update_status", methods=["POST"])
def update_status(gateway_id):
    """ 指定Gatewayのstatus更新 """

    try:
        status: str = request.json["status"]
    except KeyError:
        message: str = "Invalid request key."
        return jsonify({"error": message}), 400

    if (status is None) or (status not in ("running", "stop")):
        message: str = f"The status '{status}' is invalid."
        logger.error(message)
        return jsonify({"error": message}), 400

    gateway = Gateway.query.get(gateway_id)

    if gateway is None:
        message: str = f"The gateway '{gateway_id}' is not found."
        logger.error(message)
        return jsonify({"error": message}), 404

    try:
        gateway.status = status
        db.session.commit()
        return jsonify({}), 200
    except Exception as e:
        message: str = f"Update gateway {gateway_id} failed."
        logger.error(str(e))
        return jsonify({"error": message}), 404

