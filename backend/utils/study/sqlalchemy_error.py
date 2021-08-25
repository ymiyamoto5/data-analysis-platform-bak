# https://stackoverflow.com/questions/32922210/why-does-a-query-invoke-a-auto-flush-in-sqlalchemy

import os.path
import os
import sqlalchemy as sa
import sqlalchemy.orm as sao
import sqlalchemy.ext.declarative as sad
from sqlalchemy_utils import create_database  # type: ignore

_Base = sad.declarative_base()
session = None


class X(_Base):  # type: ignore
    __tablename__ = "X"

    _oid = sa.Column("oid", sa.Integer, primary_key=True)
    _nn = sa.Column("nn", sa.Integer, nullable=False)  # NOT NULL!
    _val = sa.Column("val", sa.Integer)

    def __init__(self, val):
        self._val = val

    def test(self, session):
        q = session.query(X).filter(X._val == self._val)
        # auto-flushを実行する。flush処理はinsertを試みる。
        x = q.one()
        # x = session.query(X).all()
        print("x={}".format(x))


dbfile = "/mnt/datadrive/tmp.db"


def _create_database():
    if os.path.exists(dbfile):
        os.remove(dbfile)

    engine = sa.create_engine("sqlite:///{}".format(dbfile), echo=True)
    create_database(engine.url)
    _Base.metadata.create_all(engine)
    return sao.sessionmaker(bind=engine)()


if __name__ == "__main__":
    session = _create_database()

    for val in range(3):
        x = X(val)
        x._nn = 0  # 必須フィールド
        session.add(x)
    session.commit()

    # 上のcommitの時点でDBには以下がinsert済み
    """
    _oid|_nn|_val
    1|0|0
    2|0|1
    3|0|2
    """

    # 更に_val = 1のデータをsessionに追加。必須フィールド_nnは未設定。
    x = X(1)
    session.add(x)

    # sessionに対してquery
    x.test(session)
