import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from src.presentation.api.main import app
from src.infrastructure.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def cleanup():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_job():
    response = client.post("/api/v1/jobs", json={"task": "Write a python script"})
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"

def test_get_jobs():
    client.post("/api/v1/jobs", json={"task": "Task 1"})
    response = client.get("/api/v1/jobs")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_frontend_loads():
    response = client.get("/")
    assert response.status_code == 200
    assert "OmniAgent Enterprise Dashboard" in response.text
