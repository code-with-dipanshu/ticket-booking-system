import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.redis import SeatHoldStore
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.role import Role  # noqa: F401
from app.models.user import User  # noqa: F401

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///./test.db"

test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)


def override_get_db():
    """Override the get_db dependency to use the test database."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Creates all tables before each test and drops them after."""
    SeatHoldStore().clear()
    Base.metadata.create_all(bind=test_engine)

    # Seed default roles for tests
    db = TestSessionLocal()
    for role_name, desc in [
        ("admin", "Administrator"),
        ("organizer", "Event organizer"),
        ("customer", "Regular customer"),
    ]:
        existing = db.query(Role).filter(Role.name == role_name).first()
        if not existing:
            db.add(Role(name=role_name, description=desc))
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client():
    """Provides a FastAPI TestClient with the test database override."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def db_session():
    """Provides a raw database session for direct DB operations in tests."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
