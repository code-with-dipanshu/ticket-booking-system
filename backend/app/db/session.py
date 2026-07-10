from typing import Generator

from app.db.database import SessionLocal


def get_db() -> Generator:
    """Dependency generator that yields a database session.

    Ensures the session is closed after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
