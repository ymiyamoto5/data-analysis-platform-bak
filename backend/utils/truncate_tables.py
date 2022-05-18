from backend.app.db.session import engine
from sqlalchemy import MetaData, event


# NOTE: 外部キー制約無効化
def _fk_pragma_off_connect(dbapi_con, con_record):
    dbapi_con.execute("pragma foreign_keys=OFF")


# NOTE: 外部キー制約有効化
def _fk_pragma_on_connect(dbapi_con, con_record):
    dbapi_con.execute("pragma foreign_keys=ON")


def truncate_tables():
    meta = MetaData(bind=engine, reflect=True)
    con = engine.connect()
    trans = con.begin()
    for table in meta.sorted_tables:
        con.execute(table.delete())
    trans.commit()


if __name__ == "__main__":
    event.listen(engine, "connect", _fk_pragma_off_connect)
    truncate_tables()
    event.listen(engine, "connect", _fk_pragma_on_connect)
