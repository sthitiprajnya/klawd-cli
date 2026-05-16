import pytest
from fastapi.testclient import TestClient
from omni_agent.api.server import app, job_store

client = TestClient(app)

def test_create_job():
    response = client.post("/api/v1/jobs", json={"task": "Write a python script"})
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"

    # Check job is in store
    job_id = data["job_id"]
    assert job_id in job_store

def test_get_job_status():
    job_id = "mock-id-123"
    job_store[job_id] = {"status": "processing", "task": "test", "result": None}

    response = client.get(f"/api/v1/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "processing"

def test_get_job_not_found():
    response = client.get("/api/v1/jobs/invalid-id")
    assert response.status_code == 404
