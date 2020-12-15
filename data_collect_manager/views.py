from types import MethodType
from data_collect_manager.models.config_file_manager import ConfigFileManager
from flask import request, render_template, g
from data_collect_manager import app


@app.route("/")
def show_manager():
    """ TOP画面表示。configファイルのstatusによって画面切り替え """

    g.running_file_path = "/home/ymiyamoto5/shared/conf_Gw-00.cnf"
    g.cfm = ConfigFileManager(g.running_file_path)

    return render_template("manager.html", is_started=g.cfm.is_running())


@app.route("/setup", methods=["POST"])
def setup():
    """ 段取り開始(rawdata取得開始) """
    # configをupdate
    # is_success: bool = g.cfm.update()
    # return {"is_success": is_success}
    return {"is_success": True}


@app.route("/start", methods=["POST"])
def start():
    """ 開始(metadataに開始時間を記録) """

    return {"is_success": True}


@app.route("/pause", methods=["POST"])
def pause():
    """ 中断(metadataに中断の開始時間を記録) """

    return {"is_success": True}


@app.route("/resume", methods=["POST"])
def resume():
    """ 再開(metadataに再開した時間を記録) """

    return {"is_success": True}


@app.route("/stop", methods=["POST"])
def stop():
    """ 停止(rawdata取得終了) """

    return {"is_success": True}


@app.route("/record_tag")
def record_tag():
    """ 事象記録 """
    pass
