from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.infrastructure.database import Base, get_db
from src.presentation.api.main import app


# ── In-memory SQLite for tests ─────────────────────────────────────────────────

SQLALCHEMY_TEST_URL = "sqlite://"  # in-memory

@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(test_engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def api_client(db_session):
    def override_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_db
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_fixture():
    return True
