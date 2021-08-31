from flask import Blueprint, jsonify
from backend.data_collect_manager.models.machine import Machine
from backend.data_collect_manager.dao.machine_dao import MachineDAO
from backend.data_collect_manager.dao.controller_dao import ControlerDAO
from backend.data_collect_manager.models.db import db
from typing import Optional, List, Tuple, Final
from datetime import datetime
import os
import time
import traceback
import glob
from backend.common.error_message import ErrorMessage, ErrorTypes
from backend.common import common
from backend.common.common_logger import logger
from backend.event_manager.event_manager import EventManager

controller = Blueprint("controller", __name__)

WAIT_SECONDS: Final[int] = 1


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

    # 基本的にUTCを使うが、events_index名のサフィックスのみJSTを使う
    utc_now: datetime = datetime.utcnow()
    jst_now: common.DisplayTime = common.DisplayTime(utc_now)

    machine: Machine = MachineDAO.select_by_id(machine_id)

    # 収集完了状態かつGW停止状態であることが前提
    is_valid, message, error_code = validation(machine, common.COLLECT_STATUS.RECORDED.value, common.STATUS.STOP.value)
    if not is_valid:
        return jsonify({"message": message}), error_code

    # events_index作成(events-<gw-id>-yyyyMMddHHMMSS(jst))
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

    # TODO: DAOへの移動およびトランザクション化
    try:
        ControlerDAO.setup(machine=machine, utc_now=utc_now)
        return jsonify({}), 200
    except Exception as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.UPDATE_FAIL, str(e))
        return jsonify({"message": message}), 500


@controller.route("/controller/start/<string:machine_id>", methods=["POST"])
def start(machine_id):
    """指定機器のデータ収集開始"""

    utc_now: datetime = datetime.utcnow()

    machine: Machine = MachineDAO.select_by_id(machine_id)

    # 段取状態かつGW開始状態であることが前提
    is_valid, message, error_code = validation(machine, common.COLLECT_STATUS.SETUP.value, common.STATUS.RUNNING.value)
    if not is_valid:
        return jsonify({"message": message}), error_code

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
        MachineDAO.update(
            machine_id=machine.machine_id, update_data={"collect_status": common.COLLECT_STATUS.START.value}
        )
        return jsonify({}), 200
    except Exception as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.UPDATE_FAIL, str(e))
        return jsonify({"message": message}), 500


@controller.route("/controller/pause/<string:machine_id>", methods=["POST"])
def pause(machine_id):
    """指定機器のデータ収集中断（中断中もデータ自体は収集されている。中断区間はショット切り出しの対象外となる。）"""

    utc_now: datetime = datetime.utcnow()

    machine: Machine = MachineDAO.select_by_id(machine_id)

    # 収集開始状態かつGW開始状態であることが前提
    is_valid, message, error_code = validation(machine, common.COLLECT_STATUS.START.value, common.STATUS.RUNNING.value)
    if not is_valid:
        return jsonify({"message": message}), error_code

    events_index: Optional[str] = EventManager.get_latest_events_index(machine_id)

    if events_index is None:
        message: str = "対象のevents_indexがありません。"
        logger.error(message)
        return jsonify({"message": message}), 500

    # events_indexに中断(pause)を記録
    successful: bool = EventManager.record_event(
        events_index, event_type=common.COLLECT_STATUS.PAUSE.value, occurred_time=utc_now
    )

    if not successful:
        message: str = "events_indexのデータ投入に失敗しました。"
        logger.error(message)
        return jsonify({"message": message}), 500

    logger.info(f"'{common.COLLECT_STATUS.PAUSE.value}' was recorded.")

    # DB更新
    try:
        MachineDAO.update(
            machine_id=machine.machine_id, update_data={"collect_status": common.COLLECT_STATUS.PAUSE.value}
        )
        return jsonify({}), 200
    except Exception as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.UPDATE_FAIL, str(e))
        return jsonify({"message": message}), 500


@controller.route("/controller/resume/<string:machine_id>", methods=["POST"])
def resume(machine_id):
    """指定機器のデータ収集再開"""

    utc_now: datetime = datetime.utcnow()

    machine: Machine = MachineDAO.select_by_id(machine_id)

    # 収集中断状態かつGW開始状態であることが前提
    is_valid, message, error_code = validation(machine, common.COLLECT_STATUS.PAUSE.value, common.STATUS.RUNNING.value)
    if not is_valid:
        return jsonify({"message": message}), error_code

    events_index: Optional[str] = EventManager.get_latest_events_index(machine_id)

    if events_index is None:
        message: str = "対象のevents_indexがありません。"
        logger.error(message)
        return jsonify({"message": message}), 500

    # events_indexの中断イベントに再開イベントを追加
    successful: bool = EventManager.update_pause_event(events_index, occurred_time=utc_now)

    if not successful:
        message: str = "events_indexのデータ更新に失敗しました。"
        logger.error(message)
        return jsonify({"message": message}), 500

    logger.info(f"'{common.COLLECT_STATUS.RESUME.value}' was recorded.")

    # DB更新
    try:
        # RESUMEはDBの状態としては保持しない。STARTに更新する。
        MachineDAO.update(
            machine_id=machine.machine_id, update_data={"collect_status": common.COLLECT_STATUS.START.value}
        )
        return jsonify({}), 200
    except Exception as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.UPDATE_FAIL, str(e))
        return jsonify({"message": message}), 500


@controller.route("/controller/stop/<string:machine_id>", methods=["POST"])
def stop(machine_id):
    """指定機器のデータ収集開始"""

    utc_now: datetime = datetime.utcnow()

    machine: Machine = MachineDAO.select_by_id(machine_id)

    # 収集開始状態かつGW開始状態であることが前提
    is_valid, message, error_code = validation(machine, common.COLLECT_STATUS.START.value, common.STATUS.RUNNING.value)
    if not is_valid:
        return jsonify({"message": message}), error_code

    events_index: Optional[str] = EventManager.get_latest_events_index(machine_id)

    if events_index is None:
        message: str = "対象のevents_indexがありません。"
        logger.error(message)
        return jsonify({"message": message}), 500

    # events_indexに収集停止(stop)を記録
    successful: bool = EventManager.record_event(
        events_index, event_type=common.COLLECT_STATUS.STOP.value, occurred_time=utc_now
    )

    if not successful:
        message: str = "events_indexのデータ投入に失敗しました。"
        logger.error(message)
        return jsonify({"message": message}), 500

    logger.info(f"'{common.COLLECT_STATUS.STOP.value}' was recorded.")

    # DB更新
    try:
        ControlerDAO.stop(machine=machine)
        return jsonify({}), 200
    except Exception as e:
        logger.error(traceback.format_exc())
        message: str = ErrorMessage.generate_message(ErrorTypes.UPDATE_FAIL, str(e))
        return jsonify({"message": message}), 500


@controller.route("/controller/check/<string:machine_id>", methods=["POST"])
def check(machine_id):
    """data_recorderによるデータ取り込みが完了したか確認。dataディレクトリにdatファイルが残っていなければ完了とみなす。"""

    machine: Machine = MachineDAO.select_by_id(machine_id)

    # 収集停止状態かつGW停止状態であることが前提
    is_valid, message, error_code = validation(machine, common.COLLECT_STATUS.STOP.value, common.STATUS.STOP.value)
    if not is_valid:
        return jsonify({"message": message}), error_code

    data_dir: str = common.get_config_value(common.APP_CONFIG_PATH, "data_dir")

    while True:
        data_file_list: List[str] = glob.glob(os.path.join(data_dir, "*.dat"))

        if len(data_file_list) != 0:
            time.sleep(WAIT_SECONDS)
            continue

        # 最新のevents_indexを取得し、記録完了イベントを記録
        events_index: Optional[str] = EventManager.get_latest_events_index(machine_id)

        if events_index is None:
            message: str = "対象のevents_indexがありません。"
            logger.error(message)
            return jsonify({"message": message}), 500

        utc_now: datetime = datetime.utcnow()

        successful: bool = EventManager.record_event(
            events_index, event_type=common.COLLECT_STATUS.RECORDED.value, occurred_time=utc_now
        )

        if not successful:
            message: str = "events_indexのデータ投入に失敗しました。"
            logger.error(message)
            return jsonify({"message": message}), 500

        logger.info(f"'{common.COLLECT_STATUS.RECORDED.value}' was recorded.")

        # DB更新
        try:
            ControlerDAO.record(machine=machine, utc_now=utc_now)
            return jsonify({}), 200
        except Exception as e:
            logger.error(traceback.format_exc())
            message: str = ErrorMessage.generate_message(ErrorTypes.UPDATE_FAIL, str(e))
            return jsonify({"message": message}), 500
