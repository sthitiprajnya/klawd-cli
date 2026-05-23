import json
from unittest.mock import MagicMock

import pytest

from src.infrastructure.memory.agent_memory import AgentMemory
from src.infrastructure.memory import optimistic_lock as lock


def test_successful_unified_write(monkeypatch):
    mem = AgentMemory()
    captured = {}

    def fake_post(_url, json=None, timeout=None):
        captured["payload"] = json
        return MagicMock(status_code=200, json=lambda: {"result": "ok"})

    monkeypatch.setattr("httpx.post", fake_post)
    record_id = mem.store_outcome(
        "task",
        "result",
        "feedback",
        job_id="j1",
        agent="a1",
        status="PASS",
        failure_class="NONE",
    )

    body = json.loads(captured["payload"]["params"]["content"])
    assert record_id.startswith("mem_")
    assert body["type"] == "workflow_outcome"
    assert body["content"]["task"] == "task"
    assert body["metadata"]["job_id"] == "j1"


def test_lock_conflict_then_retry_exhaustion(monkeypatch):
    monkeypatch.setattr(lock.agentmemory_client, "get_memory", lambda _q: "changed")
    monkeypatch.setattr(lock.agentmemory_client, "store_memory", lambda _m: None)

    sleeps = []
    monkeypatch.setattr(lock.time, "sleep", lambda s: sleeps.append(s))

    with pytest.raises(lock.RetryExhaustedError):
        lock.write_with_version_check("w", "r", "d", "new", "expected", max_retries=3, backoff_seconds=0.1)

    assert sleeps == [0.1, 0.2]


def test_successful_write_after_conflict(monkeypatch):
    states = iter(["changed", "baseline"])
    monkeypatch.setattr(lock.agentmemory_client, "get_memory", lambda _q: next(states))
    stored = {}
    monkeypatch.setattr(lock.agentmemory_client, "store_memory", lambda m: stored.setdefault("v", m))
    monkeypatch.setattr(lock.time, "sleep", lambda _s: None)

    expected = lock.hashlib.sha256("baseline".encode()).hexdigest()[:16]
    new_hash = lock.write_with_version_check("w", "r", "d", "new", expected, max_retries=2, backoff_seconds=0)

    assert new_hash == lock.hashlib.sha256("new".encode()).hexdigest()[:16]
    assert "[w:r:d] new" == stored["v"]


def test_non_fatal_persistence_failure(monkeypatch):
    mem = AgentMemory()
    monkeypatch.setattr("httpx.post", lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("boom")))

    record_id = mem.store_outcome("task", "result", "feedback")
    assert record_id.startswith("mem_")
