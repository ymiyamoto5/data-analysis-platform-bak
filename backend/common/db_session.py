from backend.app.db.session import SessionLocal
from contextlib import contextmanager


@contextmanager
def db_session():
    """クエリの度に新規セッションを作成する"""

    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
