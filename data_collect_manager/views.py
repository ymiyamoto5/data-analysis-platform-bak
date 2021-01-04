import os
import sys
from flask import render_template, request, Response
from datetime import datetime
from pytz import timezone
import json

from werkzeug import exceptions

from data_collect_manager import app
from data_collect_manager.models.config_file_manager import ConfigFileManager

sys.path.append(os.path.join(os.path.dirname(__file__), "../utils"))
from elastic_manager import ElasticManager


@app.route("/")
def show_manager():
    """ TOP画面表示。configファイルのstatusによって画面切り替え """

    cfm = ConfigFileManager()

    # conifgファイルがない場合、初期configを生成
    if not cfm.config_exists():
        successful: bool = cfm.create()
        if not successful:
            return Response(response=json.dumps({"successful": successful}), status=500)
        return render_template("manager.html", status="stop")

    # configファイルがある場合、直近のevents_indexから状態判定
    latest_event_index: str = ElasticManager.get_latest_events_index()

    # configファイルがあるのにevents_indexがない例外パターン。
    if latest_event_index is None:
        app.logger.error("config file exists, but events_index not found.")
        # stop状態にして収集を止め、初期画面に戻す
        successful: bool = cfm.update({"status": "stop"})
        if not successful:
            return Response(response=json.dumps({"successful": successful}), status=500)

        return render_template("manager.html", status="stop")

    # events_indexの最新documentから状態判定
    latest_events_index_doc: dict = ElasticManager.get_latest_events_index_doc(latest_event_index)
    event_type: str = latest_events_index_doc["event_type"]

    # pause状態の場合、pauseのままなのか再開されたかによって状態変更
    if event_type == "pause":
        if latest_events_index_doc.get("end_time") is not None:
            event_type == "start"

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
    ElasticManager.create_index(events_index)

    # events_indexに段取り開始(setup)を記録
    doc_id = 0
    query = {"event_id": doc_id, "event_type": "setup", "occurred_time": utc_now}
    successful: bool = ElasticManager.create_doc(events_index, doc_id, query)

    if not successful:
        return Response(response=json.dumps({"successful": successful}), status=500)

    # configファイル更新
    start_time: str = utc_now.strftime("%Y%m%d%H%M%S%f")
    params = {"status": "running", "start_time": start_time}
    cfm = ConfigFileManager()
    successful: bool = cfm.update(params)

    if not successful:
        return Response(response=json.dumps({"successful": successful}), status=500)

    return Response(response=json.dumps({"successful": successful}), status=200)


@app.route("/start", methods=["POST"])
def start():
    """ 開始(eventsに開始時間を記録) """

    utc_now: datetime = datetime.utcnow()

    # events_indexに開始イベントを記録
    events_index: str = ElasticManager.get_latest_events_index()
    doc_id = ElasticManager.count(events_index)
    query = {"event_id": doc_id, "event_type": "start", "occurred_time": utc_now}
    successful: bool = ElasticManager.create_doc(events_index, doc_id, query)

    if not successful:
        return Response(response=json.dumps({"successful": successful}), status=500)

    return Response(response=json.dumps({"successful": successful}), status=200)


@app.route("/pause", methods=["POST"])
def pause():
    """ 中断(eventsに中断の開始時間を記録) """

    utc_now: datetime = datetime.utcnow()

    # 中断イベントの記録。中断終了時刻は現在時刻を仮置き。
    events_index: str = ElasticManager.get_latest_events_index()
    doc_id = ElasticManager.count(events_index)
    query = {"event_id": doc_id, "event_type": "pause", "start_time": utc_now}
    successful: bool = ElasticManager.create_doc(events_index, doc_id, query)

    if not successful:
        return Response(response=json.dumps({"successful": successful}), status=500)

    return Response(response=json.dumps({"successful": successful}), status=200)


@app.route("/resume", methods=["POST"])
def resume():
    """ 再開(eventsに再開した時間を記録) """

    utc_now: datetime = datetime.utcnow()

    # 再開時は中断時に記録されたイベントを更新
    events_index: str = ElasticManager.get_latest_events_index()
    doc_id = ElasticManager.count(events_index) - 1  # 更新対象は最新のdocument（pause）イベントである前提
    query = {"end_time": utc_now}
    successful: bool = ElasticManager.update_doc(events_index, doc_id, query)

    if not successful:
        return Response(response=json.dumps({"successful": successful}), status=500)

    return Response(response=json.dumps({"successful": successful}), status=200)


@app.route("/stop", methods=["POST"])
def stop():
    """ 停止(rawdata取得終了) """

    utc_now: datetime = datetime.utcnow()

    # configファイル更新
    end_time: str = utc_now.strftime("%Y%m%d%H%M%S%f")
    params = {"status": "stop", "end_time": end_time}
    cfm = ConfigFileManager()
    successful: bool = cfm.update(params)

    if not successful:
        return Response(response=json.dumps({"successful": successful}), status=500)

    # events_indexに停止イベントを記録
    events_index: str = ElasticManager.get_latest_events_index()
    doc_id = ElasticManager.count(events_index)
    query = {"event_id": doc_id, "event_type": "stop", "occurred_time": utc_now}
    successful = ElasticManager.create_doc(events_index, doc_id, query)

    if not successful:
        return Response(response=json.dumps({"successful": successful}), status=500)

    return Response(response=json.dumps({"successful": successful}), status=200)


@app.route("/record_tag", methods=["POST"])
def record_tag():
    """ 事象記録 """

    try:
        tag: str = request.form["tag"]
    except exceptions.BadRequestKeyError as e:
        app.logger.error(str(e))
        return Response(response=json.dumps({"successful": False, "message": str(e)}), status=500)

    utc_now: datetime = datetime.utcnow()

    # events_indexに事象記録
    query = {"event_type": "tag", "tag": tag, "occurred_time": utc_now}
    events_index: str = ElasticManager.get_latest_events_index()
    doc_id = ElasticManager.count(events_index)
    successful: bool = ElasticManager.create_doc(events_index, doc_id, query)

    if not successful:
        return Response(response=json.dumps({"successful": successful, "message": "record_tag: create_doc failed."}))

    return Response(response=json.dumps({"successful": successful}), status=200)
