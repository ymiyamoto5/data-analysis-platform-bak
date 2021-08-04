from flask import Blueprint, jsonify, request
from data_collect_manager.models.gateway import Gateway
from data_collect_manager.models.db import db
import re
import logging

# TODO: data_collect_managerのloggerを引き継ぐように設定したい。
logger = logging.getLogger("data_collect_manager")

gateways = Blueprint("gateways", __name__)


@gateways.route("/gateways", methods=["GET"])
def fetch_gateways():
    """ Gatewayを起点に関連エンティティを全結合したデータを返す。"""

    gateways = Gateway.query.all()

    return jsonify(gateways)


@gateways.route("/gateways/<string:gateway_id>", methods=["GET"])
def fetch_gateway(gateway_id):
    """ 指定Gatewayの情報を取得 """

    gateway = Gateway.query.get(gateway_id)

    return jsonify(gateway)


@gateways.route("/gateways", methods=["POST"])
def create():
    """ Gatewayの作成 """

    # parameter validation
    try:
        gateway_id: str = request.json["gateway_id"]
        log_level: int = int(request.json["log_level"])
    except KeyError as e:
        message: str = f"{str(e)} が不正です。"
        logger.error(message)
        return jsonify({"message": message}), 400
    except ValueError as e:
        message: str = f"次のエラーが発生しました。{str(e)}"
        logger.error(str(e))
        return jsonify({"message": message}), 400

    gateway_id_pattern = re.compile("[a-zA-Z0-9-]+")
    if not gateway_id_pattern.fullmatch(gateway_id):
        message: str = f"gateway_id '{gateway_id}' が不正です。"
        logger.error(message)
        return jsonify({"message": message}), 400

    if log_level < 0 or log_level > 5:
        message: str = f"log_level '{log_level}' が不正です。"
        logger.error(message)
        return jsonify({"message": message}), 400

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
        return jsonify({"message": message}), 500


@gateways.route("/gateways/<string:gateway_id>/update", methods=["POST"])
def update(gateway_id):
    """ TODO: 実装
        指定Gatewayの全情報更新。同時に以下を行う。
        * sequence_numberをインクリメント
        * gateway_resultを0に初期化 """

    pass


@gateways.route("/gateways/<string:gateway_id>/update_status", methods=["POST"])
def update_status(gateway_id):
    """ 指定Gatewayのstatus更新。本APIの呼び出しはWebAPのみが行い、IoTGWは行わない。
        同時に以下を更新する。
        * sequence_numberをインクリメント
        * gateway_resultを0に初期化
    """

    try:
        status: str = request.json["status"]
    except KeyError as e:
        message: str = f"Invalid request key {str(e)}."
        return jsonify({"message": message}), 400

    if (status is None) or (status not in ("running", "stop")):
        message: str = f"status '{status}' が不正です。"
        logger.error(message)
        return jsonify({"message": message}), 400

    gateway = Gateway.query.get(gateway_id)

    if gateway is None:
        message: str = f"gateway '{gateway_id}' が見つかりません。"
        logger.error(message)
        return jsonify({"message": message}), 404

    try:
        gateway.status = status
        gateway.sequence_number += 1
        gateway.gateway_result = 0
        db.session.commit()
        return jsonify({}), 200
    except Exception as e:
        message: str = f"gateway {gateway_id} の更新に失敗しました。"
        logger.error(str(e))
        return jsonify({"message": message}), 500


@gateways.route("/gateways/<string:gateway_id>/update_result", methods=["POST"])
def update_result(gateway_id):
    """ 指定Gatewayのgateway_result更新。同時にsequence_numberも更新する。
        IoTGWは以下のように値をセットする。
        * 正常時：sequence_numberは変更しない。gateway_resultはそのときのsequence_numberを設定する。
        * IoTGW異常時(GW側起因)：sequence_numberは変更しない。gateway_resultは-1を設定する。
        * IoTGW異常時(サーバー側起因)：sequence_numberを-1、gateway_resultも-1に設定する。
    """

    # parameter validation
    try:
        sequence_number: int = int(request.json["sequence_number"])
        gateway_result: int = int(request.json["gateway_result"])
    except KeyError as e:
        message: str = f"{str(e)} が不正です。"
        logger.error(message)
        return jsonify({"message": message}), 400
    except ValueError as e:
        message: str = f"次のエラーが発生しました。{str(e)}"
        logger.error(str(e))
        return jsonify({"message": message}), 400

    if sequence_number < -1:
        message: str = f"sequence_number '{sequence_number}' が不正です。"
        logger.error(message)
        return jsonify({"message": message}), 400

    if gateway_result not in (-1, 0, 1):
        message: str = f"gateway_result '{gateway_result}' が不正です。"
        logger.error(message)
        return jsonify({"message": message}), 400

    gateway = Gateway.query.get(gateway_id)

    if gateway is None:
        message: str = f"gateway '{gateway_id}' が見つかりません。"
        logger.error(message)
        return jsonify({"message": message}), 404

    try:
        gateway.sequence_number = sequence_number
        gateway.gateway_result = gateway_result
        db.session.commit()
        return jsonify({}), 200
    except Exception as e:
        message: str = f"gateway {gateway_id} の更新に失敗しました。"
        logger.error(str(e))
        return jsonify({"message": message}), 500

