from typing import Final
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from backend.common import common
from sqlalchemy import event

app_config_path: str = common.APP_CONFIG_PATH
SQLALCHEMY_DATABASE_URI: Final[str] = common.get_config_value(app_config_path, "SQLALCHEMY_DATABASE_URI")

# NOTE: check_same_thread: False is needed only for SQLite. It's not needed for other databases.
# https://fastapi.tiangolo.com/ja/tutorial/sql-databases/
engine = create_engine(SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False}, echo=True)


# NOTE: sqliteは既定で外部キー制約無効のため有効化する
def _fk_pragma_on_connect(dbapi_con, con_record):
    dbapi_con.execute("pragma foreign_keys=ON")


event.listen(engine, "connect", _fk_pragma_on_connect)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
