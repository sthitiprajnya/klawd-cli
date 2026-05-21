import json
from unittest.mock import MagicMock

import pytest

from src.infrastructure.memory.agent_memory import AgentMemory


@pytest.fixture
def agent_memory():
    return AgentMemory()


def test_store_outcome(agent_memory, monkeypatch):
    captured = {}

    def fake_post(_url, json=None, timeout=None):
        captured["payload"] = json
        return MagicMock(status_code=200, json=lambda: {"result": "ok"})

    monkeypatch.setattr("src.infrastructure.memory.agent_memory.httpx.post", fake_post)

    record_id = agent_memory.store_outcome(
        "test task",
        "test result",
        "test feedback",
        job_id="job-123",
        agent="test-agent",
        status="SUCCESS",
        failure_class="NONE",
        metadata={"layer": "app"}
    )

    assert record_id.startswith("mem_")
    body = json.loads(captured["payload"]["params"]["content"])
    assert body["type"] == "workflow_outcome"
    assert body["content"]["task"] == "test task"
    assert body["metadata"]["job_id"] == "job-123"
    assert body["metadata"]["layer"] == "app"


def test_search_records_success(agent_memory, monkeypatch):
    def fake_post(_url, json=None, timeout=None):
        return MagicMock(
            status_code=200,
            json=lambda: {"result": [{"id": "1", "content": "res1"}, "{\"id\": \"2\", \"content\": \"res2\"}"]}
        )

    monkeypatch.setattr("src.infrastructure.memory.agent_memory.httpx.post", fake_post)

    records = agent_memory._search_records("query")
    assert len(records) == 2
    assert records[0]["id"] == "1"
    assert records[1]["id"] == "2"


def test_search_records_not_200(agent_memory, monkeypatch):
    def fake_post(_url, json=None, timeout=None):
        return MagicMock(status_code=500)

    monkeypatch.setattr("src.infrastructure.memory.agent_memory.httpx.post", fake_post)

    records = agent_memory._search_records("query")
    assert records == []


def test_search_records_invalid_json(agent_memory, monkeypatch):
    def fake_post(_url, json=None, timeout=None):
        return MagicMock(
            status_code=200,
            json=lambda: {"result": ["invalid_json_string", {"id": "1", "content": "res1"}]}
        )

    monkeypatch.setattr("src.infrastructure.memory.agent_memory.httpx.post", fake_post)

    records = agent_memory._search_records("query")
    assert len(records) == 1
    assert records[0]["id"] == "1"


def test_retrieve_lessons_success_list(agent_memory, monkeypatch):
    def fake_post(_url, json=None, timeout=None):
        return MagicMock(
            status_code=200,
            json=lambda: {"result": ["lesson 1", "lesson 2"]}
        )

    monkeypatch.setattr("src.infrastructure.memory.agent_memory.httpx.post", fake_post)

    lessons = agent_memory.retrieve_lessons("context")
    assert lessons == "lesson 1\n---\nlesson 2"


def test_retrieve_lessons_success_string(agent_memory, monkeypatch):
    def fake_post(_url, json=None, timeout=None):
        return MagicMock(
            status_code=200,
            json=lambda: {"result": "a single lesson"}
        )

    monkeypatch.setattr("src.infrastructure.memory.agent_memory.httpx.post", fake_post)

    lessons = agent_memory.retrieve_lessons("context")
    assert lessons == "a single lesson"


def test_retrieve_lessons_fallback_to_search(agent_memory, monkeypatch):
    # Retrieve API returns nothing, search API returns something
    call_count = 0
    def fake_post(_url, json=None, timeout=None):
        nonlocal call_count
        call_count += 1
        if json.get("method") == "retrieve_lessons":
            return MagicMock(status_code=200, json=lambda: {"result": []})
        elif json.get("method") == "memory_smart_search":
            return MagicMock(
                status_code=200,
                json=lambda: {"result": [{"content": "search lesson 1"}, {"content": "search lesson 2"}]}
            )
        return MagicMock(status_code=200)

    monkeypatch.setattr("src.infrastructure.memory.agent_memory.httpx.post", fake_post)

    lessons = agent_memory.retrieve_lessons("context")
    assert call_count == 2
    assert "\"search lesson 1\"" in lessons
    assert "\"search lesson 2\"" in lessons


def test_retrieve_lessons_fallback_no_results(agent_memory, monkeypatch):
    def fake_post(_url, json=None, timeout=None):
        return MagicMock(status_code=200, json=lambda: {"result": []})

    monkeypatch.setattr("src.infrastructure.memory.agent_memory.httpx.post", fake_post)

    lessons = agent_memory.retrieve_lessons("context")
    assert lessons == "No past lessons found."


def test_retrieve_lessons_exception(agent_memory, monkeypatch):
    def fake_post(_url, json=None, timeout=None):
        raise RuntimeError("boom")

    monkeypatch.setattr("src.infrastructure.memory.agent_memory.httpx.post", fake_post)

    lessons = agent_memory.retrieve_lessons("context")
    assert lessons == "Could not retrieve past lessons."
