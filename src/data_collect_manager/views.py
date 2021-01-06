import os
import sys
import time
import glob
from flask import render_template, request, Response
from datetime import datetime
from pytz import timezone
from typing import Optional, Tuple, List, Final
import json

from werkzeug import exceptions

from data_collect_manager import app

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from elastic_manager.elastic_manager import ElasticManager
from config_file_manager.config_file_manager import ConfigFileManager

sys.path.append(os.path.join(os.path.dirname(__file__), "../utils/"))
import common


def _initialize_config_file() -> Tuple[bool, Optional[str]]:
    """ 不正な状態が検出された場合、configファイルのstatusをstopにして初期化する """

    cfm = ConfigFileManager()

    successful: bool = cfm.update({"status": "stop"})

    message: str = None
    if not successful:
        message: str = "config file update failed."

    return successful, message


@app.route("/")
def show_manager():
    """ TOP画面表示。configファイルのstatusによって画面切り替え """

    cfm = ConfigFileManager()

    # conifgファイルがない場合、初期configを生成
    if not cfm.config_exists():
        successful: bool = cfm.create()
        if not successful:
            return Response(
                response=json.dumps({"successful": successful, "message": "config file create failed"}), status=500
            )

    # 直近のevents_indexから状態判定
    latest_event_index: Optional[str] = ElasticManager.get_latest_events_index()

    # 直近のevents_indexがない場合、初期化処理後に初期画面へ遷移
    if latest_event_index is None:
        successful, message = _initialize_config_file()
        if not successful:
            return Response(response=json.dumps({"successful": successful, "message": message}), status=500)
        return render_template("manager.html", status="stop")

    # events_indexの最新documentから状態判定
    latest_events_index_doc: Optional[dict] = ElasticManager.get_latest_events_index_doc(latest_event_index)

    # 最新のevents_indexがあるのにdocumentがない例外パターン
    if latest_events_index_doc is None:
        app.logger.error("events_index exists, but document not found.")
        successful, message = _initialize_config_file()
        if not successful:
            return Response(response=json.dumps({"successful": successful, "message": message}), status=500)
        return render_template("manager.html", status="stop")

    event_type: str = latest_events_index_doc["event_type"]

    # pause状態の場合、pauseのままなのか再開されたかによって状態変更
    if event_type == "pause":
        if latest_events_index_doc.get("end_time") is not None:
            event_type = "start"

    # 状態に応じて画面を戻す
    return render_template("manager.html", status=event_type)


@app.route("/setup", methods=["POST"])
def setup():
    """ 段取り開始(rawdata取得開始) """

    # 基本的にUTCを使うが、events_index名のサフィックスのみJSTを使う
    utc_now: datetime = datetime.utcnow()
    jst_now = utc_now.astimezone(timezone("Asia/Tokyo"))

    # events_index作成
    events_index: str = "events-" + jst_now.strftime("%Y%m%d%H%M%S")
    successful: bool = ElasticManager.create_index(events_index)

    if not successful:
        return Response(
            response=json.dumps({"successful": successful, "message": "create ES index failed."}), status=500
        )

    # events_indexに段取り開始(setup)を記録
    doc_id = 0
    query = {"event_id": doc_id, "event_type": "setup", "occurred_time": utc_now}
    successful: bool = ElasticManager.create_doc(events_index, doc_id, query)

    if not successful:
        return Response(response=json.dumps({"successful": successful, "message": "save to ES failed."}), status=500)

    # configファイル更新
    start_time: str = utc_now.strftime("%Y%m%d%H%M%S%f")
    params: dict = {"status": "running", "start_time": start_time}
    cfm = ConfigFileManager()
    successful: bool = cfm.update(params)

    if not successful:
        return Response(
            response=json.dumps({"successful": successful, "message": "config file update failed."}), status=500
        )

    return Response(response=json.dumps({"successful": successful}), status=200)


@app.route("/start", methods=["POST"])
def start():
    """ 開始(eventsに開始時間を記録) """

    utc_now: datetime = datetime.utcnow()

    # events_indexに開始イベントを記録
    events_index: Optional[str] = ElasticManager.get_latest_events_index()

    if events_index is None:
        app.logger.error("events_index not found.")
        successful, message = _initialize_config_file()
        if not successful:
            return Response(response=json.dumps({"successful": successful, "message": message}), status=500)
        return render_template("manager.html", status="stop")

    doc_id: int = ElasticManager.count(events_index)
    query: dict = {"event_id": doc_id, "event_type": "start", "occurred_time": utc_now}
    successful: bool = ElasticManager.create_doc(events_index, doc_id, query)

    if not successful:
        return Response(response=json.dumps({"successful": successful, "message": "save to ES failed."}), status=500)

    return Response(response=json.dumps({"successful": successful}), status=200)


@app.route("/pause", methods=["POST"])
def pause():
    """ 中断(eventsに中断の開始時間を記録) """

    utc_now: datetime = datetime.utcnow()

    # 中断イベントの記録。中断終了時刻は現在時刻を仮置き。
    events_index: Optional[str] = ElasticManager.get_latest_events_index()

    if events_index is None:
        app.logger.error("events_index not found.")
        successful, message = _initialize_config_file()
        if not successful:
            return Response(response=json.dumps({"successful": successful, "message": message}), status=500)
        return render_template("manager.html", status="stop")

    doc_id: int = ElasticManager.count(events_index)
    query: dict = {"event_id": doc_id, "event_type": "pause", "start_time": utc_now}
    successful: bool = ElasticManager.create_doc(events_index, doc_id, query)

    if not successful:
        return Response(response=json.dumps({"successful": successful, "message": "save to ES failed."}), status=500)

    return Response(response=json.dumps({"successful": successful}), status=200)


@app.route("/resume", methods=["POST"])
def resume():
    """ 再開(eventsに再開した時間を記録) """

    utc_now: datetime = datetime.utcnow()

    # 再開時は中断時に記録されたイベントを更新
    events_index: Optional[str] = ElasticManager.get_latest_events_index()

    if events_index is None:
        app.logger.error("events_index not found.")
        successful, message = _initialize_config_file()
        if not successful:
            return Response(response=json.dumps({"successful": successful, "message": message}), status=500)
        return render_template("manager.html", status="stop")

    doc_id: int = ElasticManager.count(events_index) - 1  # 更新対象は最新のdocument（pause）イベントである前提
    query: dict = {"end_time": utc_now}
    successful: bool = ElasticManager.update_doc(events_index, doc_id, query)

    if not successful:
        return Response(response=json.dumps({"successful": successful, "message": "save to ES failed."}), status=500)

    return Response(response=json.dumps({"successful": successful}), status=200)


@app.route("/stop", methods=["POST"])
def stop():
    """ 停止(rawdata取得終了) """

    utc_now: datetime = datetime.utcnow()

    # configファイル更新
    end_time: str = utc_now.strftime("%Y%m%d%H%M%S%f")
    params: dict = {"status": "stop", "end_time": end_time}
    cfm = ConfigFileManager()
    successful: bool = cfm.update(params)

    if not successful:
        return Response(
            response=json.dumps({"successful": successful, "message": "config file update failed."}), status=500
        )

    # events_indexに停止イベントを記録
    events_index: Optional[str] = ElasticManager.get_latest_events_index()

    if events_index is None:
        app.logger.error("events_index not found.")
        successful, message = _initialize_config_file()
        if not successful:
            return Response(response=json.dumps({"successful": successful, "message": message}), status=500)
        return render_template("manager.html", status="stop")

    doc_id = ElasticManager.count(events_index)
    query = {"event_id": doc_id, "event_type": "stop", "occurred_time": utc_now}
    successful = ElasticManager.create_doc(events_index, doc_id, query)

    if not successful:
        return Response(response=json.dumps({"successful": successful, "message": "save to ES failed."}), status=500)

    return Response(response=json.dumps({"successful": successful}), status=200)


@app.route("/record_tag", methods=["POST"])
def record_tag():
    """ 事象記録 """

    try:
        tag: str = request.form["tag"]
    except exceptions.BadRequestKeyError as e:
        app.logger.exception(str(e))
        return Response(response=json.dumps({"successful": False, "message": str(e)}), status=400)

    utc_now: datetime = datetime.utcnow()

    # events_indexに事象記録
    events_index: Optional[str] = ElasticManager.get_latest_events_index()

    if events_index is None:
        app.logger.error("events_index not found.")
        successful, message = _initialize_config_file()
        if not successful:
            return Response(response=json.dumps({"successful": successful, "message": message}), status=500)
        return render_template("manager.html", status="stop")

    doc_id: int = ElasticManager.count(events_index)
    query: dict = {"event_type": "tag", "tag": tag, "occurred_time": utc_now}
    successful: bool = ElasticManager.create_doc(events_index, doc_id, query)

    if not successful:
        return Response(response=json.dumps({"successful": successful, "message": "save to ES failed."}), status=500)

    return Response(response=json.dumps({"successful": successful}), status=200)


# 最大 36 * 5 = 180 秒待つ
# NOTE: ローカル変数はmockできないのでglobalで定義
RETRY_COUNT: Final[int] = 36
WAIT_SECONDS: Final[int] = 5


@app.route("/check", methods=["GET"])
def check_record_finished():
    """ data_recorderによるデータ取り込みが完了したか確認。dataディレクトリにdatファイルが残っていなければ完了とみなす。 """

    cfm = ConfigFileManager()

    data_dir: str = common.get_config_value(cfm.app_config_path, "data_dir")

    message: str = f"Wait {RETRY_COUNT * WAIT_SECONDS} sec, but data recording is not finished yet."
    successful: bool = False
    status: int = 500

    for _ in range(RETRY_COUNT):
        data_file_list: List[str] = glob.glob(os.path.join(data_dir, "*.dat"))

        if len(data_file_list) == 0:
            successful: bool = True
            message: str = "data recording is finished."
            status: int = 200
            break

        time.sleep(WAIT_SECONDS)

    return Response(response=json.dumps({"successful": successful, "message": message}), status=status)

