from data_collect_manager.models.config_file_manager import ConfigFileManager
from flask import request, render_template
from data_collect_manager import app


@app.route("/")
def show_manager():
    return render_template("manager.html")


@app.route("/start")
def start():
    # ファイル存在確認、なければファイル作成、あればフラグだけ立てる
    running_file_path = "~/shared/conf_Gw-00.cnf"
    cfm = ConfigFileManager(running_file_path)
    if not cfm.check_file_exists():
        # create running file
        pass

    is_started = True

    return render_template("manager.html", is_started=is_started)


@app.route("/record_tag")
def record_tag():
    pass
