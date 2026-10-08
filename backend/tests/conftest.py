import os
os.environ["TESTING"] = "1"

import pytest
from app.db.base import Base
from app.db.session import engine, SessionLocal

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(autouse=True)
def clear_db(db):
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()

@pytest.fixture
def db():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

from fastapi.testclient import TestClient
from app.main import app
from app.api.deps import get_current_active_user
from app.models.user import User, Role

def override_get_current_active_user():
    return User(
        id="test-user-id",
        email="test@modelsentinel.com",
        full_name="Test User",
        role=Role.ADMIN,
        is_active=True
    )

app.dependency_overrides[get_current_active_user] = override_get_current_active_user

# If there are tests that instantiate their own TestClient, they will automatically use the overridden dependency.
