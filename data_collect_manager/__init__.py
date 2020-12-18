import os
from flask import Flask
from logging.config import dictConfig
from flask_session import Session

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
            }
        },
        "root": {"level": "INFO", "handlers": ["wsgi"]},
    }
)

app = Flask(__name__)

# config
config_type = {
    "development": "data_collect_manager.config.Development",
    "testing": "data_collect_manager.config.Testing",
    "production": "data_collect_manager.config.Production",
}

app.config.from_object(config_type.get(os.getenv("FLASK_APP_ENV", "production")))

# session
app.config["SESSION_TYPE"] = "filesystem"
app.config["JSON_AS_ASCII"] = False

Session(app)

import data_collect_manager.views