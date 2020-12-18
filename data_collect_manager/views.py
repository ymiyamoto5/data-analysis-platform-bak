import os
import sys
from flask import render_template, request, Response, session
from datetime import datetime, timezone, timedelta
import json

from werkzeug import exceptions

from data_collect_manager import app
from data_collect_manager.models.config_file_manager import ConfigFileManager

sys.path.append(os.path.join(os.path.dirname(__file__), "../utils"))
from elastic_manager import ElasticManager


JST = timezone(timedelta(hours=+9), "JST")


@app.route("/")
def show_manager():
    """ TOP画面表示。configファイルのstatusによって画面切り替え """

    # TODO: ファイルの配置場所設定
    # running_file_path = "/home/ymiyamoto5/shared/conf_Gw-00.cnf"
    cfm = ConfigFileManager()

    if not cfm.config_exists:
        cfm.create({"status": "stop"})
        return render_template("manager.html", status="stop")

    # configファイルがある場合、直近のevents_indexから状態判定
    latest_event_index: str = ElasticManager.get_latest_events_index()

    # configファイルがあるのにevents_indexがない例外パターン。
    if latest_event_index is None:
        app.logger.error("config file exists, but events_index not found.")
        # stop状態にして収集を止め、初期画面に戻す
        session["events_index"] = ""
        cfm.update({"status": "stop"})
        return render_template("manager.html", status="stop")

    session["events_index"] = latest_event_index

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

    now: datetime = datetime.now(JST)

    # events_index作成
    events_index: str = "events-" + now.strftime("%Y%m%d%H%M%S")
    ElasticManager.create_index(events_index)

    session["events_index"] = events_index

    # events_indexに段取り開始(setup)を記録
    session["event_id"] = 0
    doc_id = session["event_id"]
    query = {"event_id": session["event_id"], "event_type": "setup", "start_time": now}
    successful: bool = ElasticManager.create_doc(events_index, doc_id, query)

    if not successful:
        return Response(response=json.dumps({"successful": successful}), status=500)

    # configファイル更新
    start_time: str = now.strftime("%Y%m%d%H%M%S%f")
    params = {"status": "running", "start_time": start_time}
    cfm = ConfigFileManager()
    successful: bool = cfm.update(params, should_change_sequence=True)

    if not successful:
        return Response(response=json.dumps({"successful": successful}), status=500)

    return Response(response=json.dumps({"successful": successful}), status=200)


@app.route("/start", methods=["POST"])
def start():
    """ 開始(eventsに開始時間を記録) """

    # configファイルを読み込み、events_index名を特定
    # cfm = ConfigFileManager()
    # config: dict = cfm.read_config()
    # events_index: str = config["events_index"]

    now: datetime = datetime.now()

    # events_indexに開始イベントを記録
    session["event_id"] += 1
    doc_id = session["event_id"]
    query = {"event_type": "start", "start_time": now}
    events_index: str = session["events_index"]
    successful: bool = ElasticManager.create_doc(events_index, doc_id, query)

    if not successful:
        return Response(response=json.dumps({"successful": successful}), status=500)

    return Response(response=json.dumps({"successful": successful}), status=200)


@app.route("/pause", methods=["POST"])
def pause():
    """ 中断(eventsに中断の開始時間を記録) """

    # configファイルを読み込み、events_index名を特定
    # cfm = ConfigFileManager()
    # config: dict = cfm.read_config()
    # events_index: str = config["events_index"]

    now: datetime = datetime.now()

    # 中断イベントの記録。中断終了時刻は現在時刻を仮置き。
    session["event_id"] += 1
    doc_id = session["event_id"]
    query = {"event_type": "pause", "start_time": now, "end_time": now}
    events_index: str = session["events_index"]
    successful: bool = ElasticManager.create_doc(events_index, doc_id, query)

    if not successful:
        return Response(response=json.dumps({"successful": successful}), status=500)

    return Response(response=json.dumps({"successful": successful}), status=200)


@app.route("/resume", methods=["POST"])
def resume():
    """ 再開(eventsに再開した時間を記録) """

    # configファイルを読み込み、events_index名を特定
    # cfm = ConfigFileManager()
    # config: dict = cfm.read_config()
    # events_index: str = config["events_index"]

    now: datetime = datetime.now()

    # 再開時は中断時に記録されたイベントを更新
    doc_id = session["event_id"]
    query = {"end_time": now}
    events_index: str = session["events_index"]
    successful: bool = ElasticManager.update_doc(events_index, doc_id, query)

    if not successful:
        return Response(response=json.dumps({"successful": successful}), status=500)

    return Response(response=json.dumps({"successful": successful}), status=200)


@app.route("/stop", methods=["POST"])
def stop():
    """ 停止(rawdata取得終了) """

    now: datetime = datetime.now()

    # configファイル更新
    end_time: str = now.strftime("%Y%m%d%H%M%S%f")
    params = {"status": "stop", "end_time": end_time}
    cfm = ConfigFileManager()
    successful: bool = cfm.update(params, should_change_sequence=True)

    if not successful:
        return Response(response=json.dumps({"successful": successful}), status=500)

    # config: dict = cfm.read_config()
    # events_index: str = config["events_index"]

    # events_indexに停止イベントを記録
    session["event_id"] += 1
    doc_id = session["event_id"]
    query = {"event_type": "stop", "end_time": now}
    events_index = session["events_index"]
    successful = ElasticManager.create_doc(events_index, doc_id, query)

    session["event_id"] = 0
    session["events_index"] = None

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

    # cfm = ConfigFileManager()
    # config: dict = cfm.read_config()
    # events_index: str = config["events_index"]

    now: datetime = datetime.now()

    # events_indexに事象記録
    session["event_id"] += 1
    doc_id = session["event_id"]
    query = {"event_type": "tag", "tag": tag, "start_time": now}
    events_index = session["events_index"]
    successful: bool = ElasticManager.create_doc(events_index, doc_id, query)

    if not successful:
        return Response(response=json.dumps({"successful": successful, "message": "record_tag: create_doc failed."}))

    return Response(response=json.dumps({"successful": successful}), status=200)
