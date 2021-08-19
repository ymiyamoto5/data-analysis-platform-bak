from typing import Final
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from backend.common import common


@contextmanager
def db_session():
    """クエリの度に新規セッションを作成する"""

    app_config_path: str = common.APP_CONFIG_PATH
    DB_URI: Final[str] = common.get_config_value(app_config_path, "SQLALCHEMY_DATABASE_URI")

    engine = create_engine(DB_URI, convert_unicode=True)
    connection = engine.connect()
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=True, bind=engine))

    yield db_session

    db_session.close()
    connection.close()
