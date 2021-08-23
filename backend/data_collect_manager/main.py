"""
 ==================================
  main.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

from flask import Flask, render_template
import sqlalchemy.engine
from sqlalchemy import event
from flask_cors import CORS  # type: ignore
from backend.data_collect_manager.models.db import register_db
from backend.data_collect_manager.apis.machines import machines
from backend.data_collect_manager.apis.gateways import gateways
from backend.data_collect_manager.apis.handlers import handlers
from backend.data_collect_manager.apis.sensors import sensors
from backend.data_collect_manager.apis.events import events
from backend.data_collect_manager.apis.controller import controller
from backend.data_collect_manager.apis.data_collect_history import data_collect_history

DIST_DIR = "../../frontend/dist"
DIST_STATIC_DIR = f"{DIST_DIR}/static"
DIST_IMAGE_DIR = f"{DIST_DIR}/img"

app = Flask(__name__, static_folder=DIST_STATIC_DIR, template_folder=DIST_DIR)

# NOTE: jsonifyのUnicodeエスケープを回避する
# https://datalove.hatenadiary.jp/entry/flask-jsonify-how-to-encode-japanese
app.config["JSON_AS_ASCII"] = False

db = register_db(app)
app.config["SQLALCHEMY_ECHO"] = True


@event.listens_for(sqlalchemy.engine.Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()


app.register_blueprint(machines, url_prefix="/api/v1")
app.register_blueprint(gateways, url_prefix="/api/v1")
app.register_blueprint(handlers, url_prefix="/api/v1")
app.register_blueprint(sensors, url_prefix="/api/v1")
app.register_blueprint(events, url_prefix="/api/v1")
app.register_blueprint(controller, url_prefix="/api/v1")
app.register_blueprint(data_collect_history, url_prefix="/api/v1")

CORS(app)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def index(path):
    return render_template("index.html")


if __name__ == "__main__":
    app.run()
