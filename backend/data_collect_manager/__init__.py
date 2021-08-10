import os
from flask import Flask
from flask_cors import CORS  # type: ignore
from backend.data_collect_manager.models.db import register_db
from backend.data_collect_manager.apis.machines import machines
from backend.data_collect_manager.apis.gateways import gateways
from backend.data_collect_manager.apis.handlers import handlers
from backend.data_collect_manager.apis.sensors import sensors

app = Flask(__name__)

# NOTE: jsonifyのUnicodeエスケープを回避する
# https://datalove.hatenadiary.jp/entry/flask-jsonify-how-to-encode-japanese
app.config["JSON_AS_ASCII"] = False

db = register_db(app)

app.register_blueprint(machines, url_prefix="/api/v1")
app.register_blueprint(gateways, url_prefix="/api/v1")
app.register_blueprint(handlers, url_prefix="/api/v1")
app.register_blueprint(sensors, url_prefix="/api/v1")

CORS(app)

# config
config_type = {
    "development": "data_collect_manager.config.Development",
    "testing": "data_collect_manager.config.Testing",
    "production": "data_collect_manager.config.Production",
}

app.config.from_object(config_type.get(os.getenv("FLASK_APP_ENV", "production")))

import data_collect_manager.views  # type: ignore
