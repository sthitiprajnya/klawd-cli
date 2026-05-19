import hashlib
import logging
import threading
import time
from contextlib import contextmanager

import httpx
import redis

r = redis.Redis(host="redis", port=6379, decode_responses=True)
logger = logging.getLogger("OptimisticLock")


class DrawerLockTimeout(Exception):
    pass


class StaleWriteError(Exception):
    pass


class RetryExhaustedError(Exception):
    pass


class AgentMemoryClient:
    def __init__(self):
        self.base_url = "http://agentmemory:3111"

    def get_memory(self, query: str) -> str:
        try:
            payload = {"jsonrpc": "2.0", "method": "memory_smart_search", "params": {"query": query}, "id": 1}
            response = httpx.post(self.base_url, json=payload, timeout=5.0)
            if response.status_code == 200:
                return str(response.json().get("result", ""))
            return ""
        except Exception:
            return ""

    def store_memory(self, memory_text: str):
        try:
            payload = {"jsonrpc": "2.0", "method": "memory_save", "params": {"content": memory_text}, "id": 1}
            httpx.post(self.base_url, json=payload, timeout=5.0)
        except Exception:
            pass


agentmemory_client = AgentMemoryClient()


@contextmanager
def drawer_write_lock(wing: str, room: str, hall: str, drawer_id: str):
    lock_identifier = f"{wing}:{room}:{hall}:{drawer_id}"
    lock_key = f"agentmemory:lock:{lock_identifier}"
    lock_value = f"{threading.current_thread().name}:{time.time()}"
    deadline = time.monotonic() + 10.0

    while time.monotonic() < deadline:
        if r.set(lock_key, lock_value, nx=True, ex=30):
            break
        time.sleep(0.2)
    else:
        raise DrawerLockTimeout(f"Lock timeout on {lock_key}")

    try:
        yield
    finally:
        if r.get(lock_key) == lock_value:
            r.delete(lock_key)


def _conflict_event(lock_identifier: str, expected_hash: str | None, current_hash: str, attempt: int) -> dict[str, str | int | None]:
    event = {
        "event": "optimistic_lock_conflict",
        "lock_identifier": lock_identifier,
        "expected_hash": expected_hash,
        "current_hash": current_hash,
        "attempt": attempt,
    }
    logger.warning("Optimistic lock conflict: %s", event)
    return event


def write_with_version_check(
    wing: str,
    room: str,
    drawer_id: str,
    new_content: str,
    expected_hash: str | None,
    *,
    max_retries: int = 3,
    backoff_seconds: float = 0.05,
) -> str:
    lock_identifier = f"{wing}:{room}:{drawer_id}"
    for attempt in range(1, max_retries + 1):
        current = agentmemory_client.get_memory(lock_identifier)
        current_hash = hashlib.sha256(current.encode()).hexdigest()[:16] if current else "empty"

        if expected_hash and current_hash != expected_hash:
            _conflict_event(lock_identifier, expected_hash, current_hash, attempt)
            if attempt >= max_retries:
                raise RetryExhaustedError("Optimistic lock retries exhausted")
            time.sleep(backoff_seconds * attempt)
            continue

        new_hash = hashlib.sha256(new_content.encode()).hexdigest()[:16]
        agentmemory_client.store_memory(f"[{lock_identifier}] {new_content}")
        return new_hash

    raise StaleWriteError("Memory modified by another agent. Re-read and retry.")
