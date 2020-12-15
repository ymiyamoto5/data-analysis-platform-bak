from data_collect_manager.models.config_file_manager import ConfigFileManager
from flask import render_template
from data_collect_manager import app


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

    params = {"status": "running"}

    cfm = ConfigFileManager()
    is_success: bool = cfm.init_config(params)

    return {"is_success": is_success}


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
