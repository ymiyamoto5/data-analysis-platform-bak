import os
from typing import Final

from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URI: Final[str] = os.environ["SQLALCHEMY_DATABASE_URI"]
DB_SQL_ECHO: Final[str] = os.environ["DB_SQL_ECHO"]

# NOTE: check_same_thread: False is needed only for SQLite. It's not needed for other databases.
# https://fastapi.tiangolo.com/ja/tutorial/sql-databases/
engine = create_engine(SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False}, echo=int(DB_SQL_ECHO))


# NOTE: sqliteは既定で外部キー制約無効のため有効化する
def _fk_pragma_on_connect(dbapi_con, con_record):
    dbapi_con.execute("pragma foreign_keys=ON")


event.listen(engine, "connect", _fk_pragma_on_connect)

SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

Base = declarative_base()
