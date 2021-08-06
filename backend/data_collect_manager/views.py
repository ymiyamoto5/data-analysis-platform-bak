"""
 ==================================
  views.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import os
import time
import glob
from flask import render_template, request, Response
from datetime import datetime
from typing import Optional, Tuple, List, Final
import json
from werkzeug import exceptions
from backend.data_collect_manager import app
from backend.event_manager.event_manager import EventManager
from backend.config_file_manager.config_file_manager import ConfigFileManager
from backend.common import common


def _initialize_config_file() -> Tuple[bool, Optional[str]]:
    """不正な状態が検出された場合、configファイルを初期化する"""

    cfm = ConfigFileManager()

    successful: bool = cfm.create()

    message: Optional[str] = None
    if not successful:
        message = "config file update failed."

    return successful, message


@app.route("/")
def show_manager():
    """TOP画面表示。configファイルのstatusによって画面切り替え"""

    cfm = ConfigFileManager()

    # conifgファイルがない場合、初期configを生成
    if not cfm.config_exists():
        message = "config file create failed"
        successful, message = _initialize_config_file()
        if not successful:
            return Response(response=json.dumps({"successful": successful, "message": message}), status=500)

    # configファイルのgateway_resultが-1のときはconfigファイルを初期化後に初期画面へ遷移
    config: dict = cfm.read_config()
    if config["gateway_result"] == -1:
        message = "The gateway status is abnormal. Initialize config."
        app.logger.error(message)
        successful, message = _initialize_config_file()
        if not successful:
            return Response(response=json.dumps({"successful": successful, "message": message}), status=500)
        return render_template("manager.html", status="stop")

    # 直近のevents_indexから状態判定
    latest_event_index: Optional[str] = EventManager.get_latest_events_index()

    # 直近のevents_indexがない場合、初期化処理後に初期画面へ遷移
    if latest_event_index is None:
        successful, message = _initialize_config_file()
        if not successful:
            return Response(response=json.dumps({"successful": successful, "message": message}), status=500)
        return render_template("manager.html", status="stop")

    # events_indexの最新documentから状態判定
    latest_events_index_docs: List[dict] = EventManager.get_latest_event(latest_event_index)

    # 最新のevents_indexがあるのにdocumentがない例外パターン
    if len(latest_events_index_docs) == 0:
        app.logger.error("events_index exists, but document not found.")
        successful, message = _initialize_config_file()
        if not successful:
            return Response(response=json.dumps({"successful": successful, "message": message}), status=500)
        return render_template("manager.html", status="stop")

    event_type: str = latest_events_index_docs[0]["event_type"]

    # pause状態の場合、pauseのままなのか再開されたかによって状態変更
    if event_type == "pause":
        if latest_events_index_docs[0].get("end_time") is not None:
            event_type = "start"

    # 状態に応じて画面を戻す
    return render_template("manager.html", status=event_type)


@app.route("/setup", methods=["POST"])
def setup():
    """段取り開始(rawdata取得開始)"""

    # 基本的にUTCを使うが、events_index名のサフィックスのみJSTを使う
    utc_now: datetime = datetime.utcnow()
    jst_now: common.DisplayTime = common.DisplayTime(utc_now)

    # 現在日時名のevents_index作成
    successful: bool
    events_index: str
    successful, events_index = EventManager.create_events_index(jst_now.to_string())

    if not successful:
        return Response(
            response=json.dumps({"successful": successful, "message": "create ES index failed."}), status=500
        )

    # events_indexに段取り開始(setup)を記録
    successful: bool = EventManager.record_event(events_index, event_type="setup", occurred_time=utc_now)

    if not successful:
        return Response(response=json.dumps({"successful": successful, "message": "save to ES failed."}), status=500)

    # configファイル更新
    params: dict = {"status": "running"}
    cfm = ConfigFileManager()
    successful: bool = cfm.update(params)

    # configファイルのgateway_resultが-1のときは設定エラーのため初期化して更新リトライ
    config: dict = cfm.read_config()
    if config["gateway_result"] == -1:
        message = "The gateway status is abnormal. Initialize config."
        app.logger.error(message)
        successful, message = _initialize_config_file()
        if not successful:
            return Response(response=json.dumps({"successful": successful, "message": message}), status=500)
        successful: bool = cfm.update(params)

    if not successful:
        return Response(
            response=json.dumps({"successful": successful, "message": "config file update failed."}), status=500
        )

    return Response(response=json.dumps({"successful": successful}), status=200)


@app.route("/start", methods=["POST"])
def start():
    """開始(eventsに開始時間を記録)"""

    utc_now: datetime = datetime.utcnow()

    events_index: Optional[str] = EventManager.get_latest_events_index()

    if events_index is None:
        app.logger.error("events_index not found.")
        successful, message = _initialize_config_file()
        if not successful:
            return Response(response=json.dumps({"successful": successful, "message": message}), status=500)
        return render_template("manager.html", status="stop")

    # events_indexに開始イベントを記録
    successful: bool = EventManager.record_event(events_index, event_type="start", occurred_time=utc_now)

    if not successful:
        return Response(response=json.dumps({"successful": successful, "message": "save to ES failed."}), status=500)

    return Response(response=json.dumps({"successful": successful}), status=200)


@app.route("/pause", methods=["POST"])
def pause():
    """中断(eventsに中断の開始時間を記録)"""

    utc_now: datetime = datetime.utcnow()

    events_index: Optional[str] = EventManager.get_latest_events_index()

    if events_index is None:
        app.logger.error("events_index not found.")
        successful, message = _initialize_config_file()
        if not successful:
            return Response(response=json.dumps({"successful": successful, "message": message}), status=500)
        return render_template("manager.html", status="stop")

    # 中断イベントの記録。中断終了時刻は現在時刻を仮置き。
    successful: bool = EventManager.record_event(events_index, event_type="pause", occurred_time=utc_now)

    if not successful:
        return Response(response=json.dumps({"successful": successful, "message": "save to ES failed."}), status=500)

    return Response(response=json.dumps({"successful": successful}), status=200)


@app.route("/resume", methods=["POST"])
def resume():
    """再開(eventsに再開した時間を記録)"""

    utc_now: datetime = datetime.utcnow()

    # 再開時は中断時に記録されたイベントを更新
    events_index: Optional[str] = EventManager.get_latest_events_index()

    if events_index is None:
        app.logger.error("events_index not found.")
        successful, message = _initialize_config_file()
        if not successful:
            return Response(response=json.dumps({"successful": successful, "message": message}), status=500)
        return render_template("manager.html", status="stop")

    successful: bool = EventManager.update_pause_event(events_index, occurred_time=utc_now)

    if not successful:
        return Response(response=json.dumps({"successful": successful, "message": "save to ES failed."}), status=500)

    return Response(response=json.dumps({"successful": successful}), status=200)


@app.route("/stop", methods=["POST"])
def stop():
    """停止(rawdata取得終了)"""

    utc_now: datetime = datetime.utcnow()

    # configファイル更新
    params: dict = {"status": "stop"}
    cfm = ConfigFileManager()
    successful: bool = cfm.update(params)

    # configファイルのgateway_resultが-1のときは設定エラーのため初期化して更新リトライ
    config: dict = cfm.read_config()
    if config["gateway_result"] == -1:
        message = "The gateway status is abnormal. Initialize config."
        app.logger.error(message)
        successful, message = _initialize_config_file()
        if not successful:
            return Response(response=json.dumps({"successful": successful, "message": message}), status=500)
        successful: bool = cfm.update(params)

    if not successful:
        return Response(
            response=json.dumps({"successful": successful, "message": "config file update failed."}), status=500
        )

    # events_indexに停止イベントを記録
    events_index: Optional[str] = EventManager.get_latest_events_index()

    if events_index is None:
        app.logger.error("events_index not found.")
        successful, message = _initialize_config_file()
        if not successful:
            return Response(response=json.dumps({"successful": successful, "message": message}), status=500)
        return render_template("manager.html", status="stop")

    successful: bool = EventManager.record_event(events_index, event_type="stop", occurred_time=utc_now)

    if not successful:
        return Response(response=json.dumps({"successful": successful, "message": "save to ES failed."}), status=500)

    return Response(response=json.dumps({"successful": successful}), status=200)


@app.route("/record_tag", methods=["POST"])
def record_tag():
    """事象記録"""

    try:
        tag: str = request.form["tag"]
    except exceptions.BadRequestKeyError as e:
        app.logger.exception(str(e))
        return Response(response=json.dumps({"successful": False, "message": str(e)}), status=400)

    utc_now: datetime = datetime.utcnow()

    # events_indexに事象記録
    events_index: Optional[str] = EventManager.get_latest_events_index()

    if events_index is None:
        app.logger.error("events_index not found.")
        successful, message = _initialize_config_file()
        if not successful:
            return Response(response=json.dumps({"successful": successful, "message": message}), status=500)
        return render_template("manager.html", status="stop")

    successful: bool = EventManager.record_tag_event(events_index, tag=tag, occurred_time=utc_now)

    if not successful:
        return Response(response=json.dumps({"successful": successful, "message": "save to ES failed."}), status=500)

    return Response(response=json.dumps({"successful": successful}), status=200)


# NOTE: ローカル変数はmockできないのでglobalで定義
WAIT_SECONDS: Final[int] = 1


@app.route("/check", methods=["GET"])
def check_record_finished():
    """data_recorderによるデータ取り込みが完了したか確認。dataディレクトリにdatファイルが残っていなければ完了とみなす。"""

    data_dir: str = common.get_config_value(common.APP_CONFIG_PATH, "data_dir")

    while True:
        data_file_list: List[str] = glob.glob(os.path.join(data_dir, "*.dat"))

        if len(data_file_list) == 0:
            successful: bool = True

            # events_indexに記録完了イベントを記録
            events_index: Optional[str] = EventManager.get_latest_events_index()

            if events_index is None:
                app.logger.error("events_index not found.")
                successful, message = _initialize_config_file()
                if not successful:
                    return Response(response=json.dumps({"successful": successful, "message": message}), status=500)
                return render_template("manager.html", status="recorded")

            utc_now: datetime = datetime.utcnow()
            successful: bool = EventManager.record_event(events_index, event_type="recorded", occurred_time=utc_now)

            if not successful:
                return Response(
                    response=json.dumps({"successful": successful, "message": "save to ES failed."}), status=500
                )

            return Response(
                response=json.dumps({"successful": successful, "message": "data recording is finished."}), status=200
            )

        time.sleep(WAIT_SECONDS)
