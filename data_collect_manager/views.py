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

    return render_template("manager.html", is_started=cfm.is_running())


@app.route("/setup", methods=["POST"])
def setup():
    """ 段取り開始(rawdata取得開始) """

    # meta_index名をconfigに保持する
    now: datetime = datetime.now(JST)
    meta_index: str = "metadata-" + now.strftime("%Y%m%d%H%M%S")

    params = {"status": "running", "meta_index": meta_index}

    cfm = ConfigFileManager()
    # configファイルがなければ作成、あれば更新
    successful: bool = cfm.init_config(params)

    if not successful:
        return Response(response=json.dumps({"successful": successful}), status=500)

    # metaインデックスがなければ作成
    if not ElasticManager.exists_index(meta_index):
        successful = ElasticManager.create_index(meta_index)

    if not successful:
        return Response(response=json.dumps({"successful": successful}), status=500)

    # metaインデックスに段取り開始を記録
    session["event_id"] = 0
    doc_id = session["event_id"]
    query = {"event_type": "setup", "setup_time": datetime.now()}
    successful: bool = ElasticManager.create_doc(meta_index, doc_id, query)

    if not successful:
        return Response(response=json.dumps({"successful": successful}), status=500)

    return Response(response=json.dumps({"successful": successful}), status=200)


@app.route("/start", methods=["POST"])
def start():
    """ 開始(metadataに開始時間を記録) """

    # configファイルを読み込み、meta_index名を特定
    cfm = ConfigFileManager()
    config: dict = cfm.read_config()
    meta_index: str = config["meta_index"]

    # meta_indexに開始イベントを記録
    session["event_id"] += 1
    doc_id = session["event_id"]
    query = {"event_type": "start", "start_time": datetime.now()}
    successful: bool = ElasticManager.create_doc(meta_index, doc_id, query)

    if not successful:
        return Response(response=json.dumps({"successful": successful}), status=500)

    return Response(response=json.dumps({"successful": successful}), status=200)


@app.route("/pause", methods=["POST"])
def pause():
    """ 中断(metadataに中断の開始時間を記録) """

    # configファイルを読み込み、meta_index名を特定
    cfm = ConfigFileManager()
    config: dict = cfm.read_config()
    meta_index: str = config["meta_index"]

    # 中断イベントの記録。中断終了時刻は現在時刻を仮置き。
    session["event_id"] += 1
    doc_id = session["event_id"]
    query = {"event_type": "pause", "start_time": datetime.now(), "end_time": datetime.now()}
    successful: bool = ElasticManager.create_doc(meta_index, doc_id, query)

    if not successful:
        return Response(response=json.dumps({"successful": successful}), status=500)

    return Response(response=json.dumps({"successful": successful}), status=200)


@app.route("/resume", methods=["POST"])
def resume():
    """ 再開(metadataに再開した時間を記録) """

    # configファイルを読み込み、meta_index名を特定
    cfm = ConfigFileManager()
    config: dict = cfm.read_config()
    meta_index: str = config["meta_index"]

    # 再開時は中断時に記録されたイベントを更新
    doc_id = session["event_id"]
    query = {"end_time": datetime.now()}
    successful: bool = ElasticManager.update_doc(meta_index, doc_id, query)

    if not successful:
        return Response(response=json.dumps({"successful": successful}), status=500)

    return Response(response=json.dumps({"successful": successful}), status=200)


@app.route("/stop", methods=["POST"])
def stop():
    """ 停止(rawdata取得終了) """

    params = {"status": "stop"}

    cfm = ConfigFileManager()
    successful: bool = cfm.update(params)

    if not successful:
        return Response(response=json.dumps({"successful": successful}), status=500)

    config: dict = cfm.read_config()
    meta_index: str = config["meta_index"]

    # meta_indexに停止イベントを記録
    session["event_id"] += 1
    doc_id = session["event_id"]
    query = {"event_type": "stop", "stop_time": datetime.now()}
    successful = ElasticManager.create_doc(meta_index, doc_id, query)

    session["event_id"] = 0

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

    cfm = ConfigFileManager()
    config: dict = cfm.read_config()
    meta_index: str = config["meta_index"]

    # meta_indexに事象記録
    session["event_id"] += 1
    doc_id = session["event_id"]
    query = {"event_type": "tag", "tag": tag, "start_time": datetime.now()}
    successful: bool = ElasticManager.create_doc(meta_index, doc_id, query)

    if not successful:
        return Response(response=json.dumps({"successful": successful, "message": "record_tag: create_doc failed."}))

    return Response(response=json.dumps({"successful": successful}), status=200)
