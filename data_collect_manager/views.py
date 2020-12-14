from flask import request, render_template
from data_collect_manager import app


@app.route("/")
def show_manager():
    return render_template("manager.html")


@app.route("/start")
def start():
    pass


@app.route("/record_tag")
def record_tag():
    pass
