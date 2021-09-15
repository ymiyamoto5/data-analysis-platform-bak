from typing import Final
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from backend.common import common

app_config_path: str = common.APP_CONFIG_PATH

SQLALCHEMY_DATABASE_URI: Final[str] = common.get_config_value(app_config_path, "SQLALCHEMY_DATABASE_URI")

# NOTE: check_same_thread: False is needed only for SQLite. It's not needed for other databases.
# https://fastapi.tiangolo.com/ja/tutorial/sql-databases/
engine = create_engine(SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False}, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
