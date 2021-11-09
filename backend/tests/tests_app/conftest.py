"""
 ==================================
  conftest.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import pytest
from backend.app.api.deps import get_db
from backend.app.db.session import Base
from backend.app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

DB_URL = "sqlite:////mnt/datadrive/temp.db"


@pytest.fixture
def client():
    """APIのクライアントのfixture。DBはtemp.dbとして用意する。"""

    client = TestClient(app)

    engine = create_engine(DB_URL, echo=True)

    # NOTE: sqliteは既定で外部キー制約無効のため有効化する
    def _fk_pragma_on_connect(dbapi_con, con_record):
        dbapi_con.execute("pragma foreign_keys=ON")

    event.listen(engine, "connect", _fk_pragma_on_connect)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # テスト用DBを初期化（関数ごとにリセット）
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # TODO: データ投入実装
    create_testdb()

    # DIを使ってFastAPIのDBの向き先をテスト用DBに変更
    def get_test_db():
        try:
            db = SessionLocal()
            yield db
        finally:
            db.close

    app.dependency_overrides[get_db] = get_test_db

    yield client


def create_testdb():
    # TODO: データ投入実装
    pass
