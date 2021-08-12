from flask import Blueprint, jsonify, request
from marshmallow import Schema, fields, ValidationError, validate
from backend.data_collect_manager.models.machine import Machine
from backend.data_collect_manager.models.gateway import Gateway
from backend.data_collect_manager.models.db import db
from typing import Optional, List, Tuple
from datetime import datetime
import traceback
from backend.common.error_message import ErrorMessage, ErrorTypes
from backend.common import common
from backend.common.common_logger import logger
from backend.event_manager.event_manager import EventManager

controller = Blueprint("controller", __name__)


def validation(machine: Machine, collect_status: str, status) -> Tuple[bool, Optional[str], int]:
    """machineとmachineに紐づくgatewayのvalidation
    * Noneでないこと
    * 対応するGatewayが1つ以上あること
    * 収集ステータスが正しいこと
    * gateway_resultが-1でないこと
    * GWステータスが正しいこと
    """

    if machine is None:
        message: str = ErrorMessage.generate_message(ErrorTypes.NOT_EXISTS)
        logger.error(message)
        return False, message, 404

    if len(machine.gateways) == 0:
        message = ErrorMessage.generate_message(ErrorTypes.NO_DATA)
        logger.error(message)
        return False, message, 404

    if machine.collect_status != collect_status:
        message = ErrorMessage.generate_message(ErrorTypes.GW_STATUS_ERROR, machine.collect_status)
        logger.error(message)
        return False, message, 500

    for gateway in machine.gateways:
        if gateway.gateway_result == -1:
            message = ErrorMessage.generate_message(ErrorTypes.GW_RESULT_ERROR, gateway.gateway_result)
            logger.error(message)
            return False, message, 500

        if gateway.status != status:
            message = ErrorMessage.generate_message(ErrorTypes.GW_STATUS_ERROR, gateway.status)
            logger.error(message)
            return False, message, 500

    return True, None, 200


@controller.route("/controller/setup/<string:machine_id>", methods=["POST"])
def setup(machine_id):
    """指定機器のデータ収集段取開始"""

    machine: Machine = Machine.query.get(machine_id)

    # 収集完了状態かつGW停止状態であることが前提
    is_valid, message, error_code = validation(machine, common.COLLECT_STATUS.RECORDED.value, common.STATUS.STOP.value)
    if not is_valid:
        return jsonify({"message": message}), error_code

    # events_index作成(events-<gw-id>-yyyyMMddHHMMSS(jst))
    # 基本的にUTCを使うが、events_index名のサフィックスのみJSTを使う
    utc_now: datetime = datetime.utcnow()
    jst_now: common.DisplayTime = common.DisplayTime(utc_now)

    # 現在日時名のevents_index作成
    successful: bool
    events_index: str
    successful, events_index = EventManager.create_events_index(machine.machine_id, jst_now.to_string())

    if not successful:
        message: str = "events_indexの作成に失敗しました。"
        logger.error(message)
        return jsonify({"message": message}), 500

    logger.info(f"{events_index} was created.")

    # events_indexに段取り開始(setup)を記録
    successful: bool = EventManager.record_event(
        events_index, event_type=common.COLLECT_STATUS.SETUP.value, occurred_time=utc_now
    )

    if not successful:
        message: str = "events_indexのデータ投入に失敗しました。"
        logger.error(message)
        return jsonify({"message": message}), 500

    logger.info(f"'{common.COLLECT_STATUS.SETUP.value}' was recorded.")

    # DB更新
    try:
        machine.collect_status = common.COLLECT_STATUS.SETUP.value
        for gateway in machine.gateways:
            gateway.sequence_number += 1
            gateway.status = common.STATUS.RUNNING.value
        db.session.commit()
        return jsonify({}), 200
    except Exception as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.UPDATE_FAIL, str(e))
        return jsonify({"message": message}), 500


@controller.route("/controller/start/<string:machine_id>", methods=["POST"])
def start(machine_id):
    """指定機器のデータ収集開始"""

    machine = Machine.query.get(machine_id)

    # 段取状態かつGW開始状態であることが前提
    is_valid, message, error_code = validation(machine, common.COLLECT_STATUS.SETUP.value, common.STATUS.RUNNING.value)
    if not is_valid:
        return jsonify({"message": message}), error_code

    utc_now: datetime = datetime.utcnow()

    events_index: Optional[str] = EventManager.get_latest_events_index(machine_id)

    if events_index is None:
        message: str = "対象のevents_indexがありません。"
        logger.error(message)
        return jsonify({"message": message}), 500

    # events_indexに収集開始(start)を記録
    successful: bool = EventManager.record_event(
        events_index, event_type=common.COLLECT_STATUS.START.value, occurred_time=utc_now
    )

    if not successful:
        message: str = "events_indexのデータ投入に失敗しました。"
        logger.error(message)
        return jsonify({"message": message}), 500

    logger.info(f"'{common.COLLECT_STATUS.START.value}' was recorded.")

    # DB更新
    try:
        machine.collect_status = common.COLLECT_STATUS.START.value
        db.session.commit()
        return jsonify({}), 200
    except Exception as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.UPDATE_FAIL, str(e))
        return jsonify({"message": message}), 500
