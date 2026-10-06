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
