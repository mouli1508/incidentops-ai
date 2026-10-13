
from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise
