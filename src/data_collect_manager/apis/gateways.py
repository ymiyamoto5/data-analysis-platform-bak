from flask import Blueprint, jsonify, request
from data_collect_manager.models.gateway import Gateway
from data_collect_manager.models.db import db
import re
import logging

# TODO: data_collect_managerのloggerを引き継ぐように設定したい。
logger = logging.getLogger("data_collect_manager")

gateways = Blueprint("gateways", __name__)


@gateways.route("/gateway", methods=["GET"])
def fetch_gateways():
    """ Gatewayを起点に関連エンティティを全結合したデータを返す。"""

    gateways = Gateway.query.all()

    return jsonify(gateways)


@gateways.route("/gateway/<string:gateway_id>", methods=["GET"])
def fetch_gateway(gateway_id):
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

    # parameter validation
    try:
        gateway_id: str = request.json["gateway_id"]
        log_level: int = int(request.json["log_level"])
    except KeyError as e:
        message: str = f"{str(e)} が不正です。"
        logger.error(message)
        return jsonify({"error": message}), 400
    except ValueError as e:
        message: str = f"次のエラーが発生しました。{str(e)}"
        logger.error(str(e))
        return jsonify({"error": message}), 400

    gateway_id_pattern = re.compile("[a-zA-Z0-9-]+")
    if not gateway_id_pattern.fullmatch(gateway_id):
        message: str = f"gateway_id '{gateway_id}' が不正です。"
        logger.error(message)
        return jsonify({"error": message}), 400

    if log_level < 0 and log_level > 5:
        message: str = f"log_level '{log_level}' が不正です。"
        logger.error(message)
        return jsonify({"error": message}), 400

    new_gateway = Gateway(
        gateway_id=gateway_id, sequence_number=1, gateway_result=0, status="stop", log_level=log_level
    )

    try:
        db.session.add(new_gateway)
        db.session.commit()
        return jsonify({}), 200
    except Exception as e:
        message: str = f"ゲートウェイ '{gateway_id}' の作成に失敗しました。"
        logger.error(str(e))
        return jsonify({"error": message}), 500


@gateways.route("/gateway/<string:gateway_id>/update_status", methods=["POST"])
def update_status(gateway_id):
    """ 指定Gatewayのstatus更新。同時にsequence_numberがインクリメントされる。 """

    try:
        status: str = request.json["status"]
    except KeyError as e:
        message: str = f"Invalid request key {str(e)}."
        return jsonify({"error": message}), 400

    if (status is None) or (status not in ("running", "stop")):
        message: str = f"status '{status}' が不正です。"
        logger.error(message)
        return jsonify({"error": message}), 400

    gateway = Gateway.query.get(gateway_id)

    if gateway is None:
        message: str = f"gateway '{gateway_id}' が見つかりません。"
        logger.error(message)
        return jsonify({"error": message}), 404

    try:
        gateway.status = status
        gateway.sequence_number += 1
        db.session.commit()
        return jsonify({}), 200
    except Exception as e:
        message: str = f"gateway {gateway_id} の更新に失敗しました。"
        logger.error(str(e))
        return jsonify({"error": message}), 500

