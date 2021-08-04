import os
import sys
from flask import Flask
from flask_cors import CORS  # type: ignore
from logging.config import dictConfig
from data_collect_manager.models.db import register_db
from data_collect_manager.apis.machines import machines
from data_collect_manager.apis.gateways import gateways

sys.path.append(os.path.join(os.path.dirname(__file__), "../utils"))
import common

LOG_FILE = os.path.join(
    common.get_config_value(common.APP_CONFIG_PATH, "log_dir"), "data_collect_manager/data_collect_manager.log"
)

# logging
dictConfig(
    {
        "version": 1,
        "formatters": {"default": {"format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"}},
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": LOG_FILE,
                "formatter": "default",
                "encoding": "utf-8",
                "maxBytes": common.MAX_LOG_SIZE,
                "backupCount": common.BACKUP_COUNT,
            },
        },
        "root": {"level": "INFO", "handlers": ["wsgi", "file"]},
    }
)

app = Flask(__name__)

# NOTE: jsonifyのUnicodeエスケープを回避する
# https://datalove.hatenadiary.jp/entry/flask-jsonify-how-to-encode-japanese
app.config["JSON_AS_ASCII"] = False

db = register_db(app)

app.register_blueprint(machines, url_prefix="/api/v1")
app.register_blueprint(gateways, url_prefix="/api/v1")

CORS(app)

# config
config_type = {
    "development": "data_collect_manager.config.Development",
    "testing": "data_collect_manager.config.Testing",
    "production": "data_collect_manager.config.Production",
}

app.config.from_object(config_type.get(os.getenv("FLASK_APP_ENV", "production")))

import data_collect_manager.views  # noqa
