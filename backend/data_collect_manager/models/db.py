from backend.common import common
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def register_db(app):
    app_config_path: str = common.APP_CONFIG_PATH

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = common.get_config_value(app_config_path, "SQLALCHEMY_DATABASE_URI")
    db.init_app(app)

    # see: https://flask-sqlalchemy.palletsprojects.com/en/2.x/contexts/
    # No application found. Either work inside a view function or push an application context.
    app.app_context().push()

    return db
