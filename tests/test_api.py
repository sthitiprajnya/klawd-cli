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
    response = client.post("/api/v1/jobs", json={"task": "Write a python script", "priority": "high", "tags": ["api", "test"]})
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"
    assert data["priority"] == "high"
    assert data["tags"] == ["api", "test"]
    assert "queue_position" in data
    assert "queue_depth" in data

def test_get_jobs():
    client.post("/api/v1/jobs", json={"task": "Task 1"})
    response = client.get("/api/v1/jobs")
    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"jobs", "total", "limit", "offset"}
    assert body["total"] == 1
    assert len(body["jobs"]) == 1

def test_get_job_by_id():
    create_response = client.post("/api/v1/jobs", json={"task": "Task 1"})
    job_id = create_response.json()["job_id"]
    response = client.get(f"/api/v1/jobs/{job_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["job_id"] == job_id
    assert body["status"] in {"pending", "processing", "completed", "failed"}
    assert "task" in body
    assert "result" in body

def test_health_and_memory_routes():
    health_response = client.get("/api/v1/health")
    assert health_response.status_code == 200
    assert "services" in health_response.json()

    memory_response = client.get("/api/v1/memory/search", params={"q": "python"})
    assert memory_response.status_code == 200
    assert memory_response.json()["query"] == "python"

def test_frontend_loads():
    response = client.get("/")
    assert response.status_code == 200
    assert "OmniAgent Enterprise Dashboard" in response.text

def test_websocket():
    with client.websocket_connect("/ws/jobs") as websocket:
        assert websocket is not None
