from flask import render_template, Response
from datetime import datetime, timezone, timedelta
import json

from data_collect_manager import app
from data_collect_manager.models.metadata_recorder import MetaDataRecorder
from data_collect_manager.models.config_file_manager import ConfigFileManager

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
        return Response(response=json.dumps(successful), status=500)

    return Response(response=json.dumps(successful), status=200)


@app.route("/start", methods=["POST"])
def start():
    """ 開始(metadataに開始時間を記録) """

    cfm = ConfigFileManager()
    config: dict = cfm.read_config()

    mdr = MetaDataRecorder()
    successful: bool = mdr.create_index(config["meta_index"])

    if not successful:
        return Response(response=json.dumps(successful), status=500)

    return Response(response=json.dumps(successful), status=200)


@app.route("/pause", methods=["POST"])
def pause():
    """ 中断(metadataに中断の開始時間を記録) """

    return {"successful": True}


@app.route("/resume", methods=["POST"])
def resume():
    """ 再開(metadataに再開した時間を記録) """

    return {"successful": True}


@app.route("/stop", methods=["POST"])
def stop():
    """ 停止(rawdata取得終了) """

    params = {"status": "stop"}

    cfm = ConfigFileManager()
    successful: bool = cfm.update(params)

    if not successful:
        return Response(response=json.dumps(successful), status=500)

    return Response(response=json.dumps(successful), status=200)


@app.route("/record_tag")
def record_tag():
    """ 事象記録 """
    pass
