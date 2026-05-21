import hashlib
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any

import httpx

logger = logging.getLogger("FailureClassifier")

FAILURE_CLASSES = {
    "FLAKE": ["connection reset by peer", "rate limit", "network unreachable", "timeout"],
    "INFRA": ["no space left on device", "oom kill", "permission denied", "disk full"],
    "LOGIC": ["assertionerror", "typeerror", "expected but got", "test_", "traceback"],
}

MAX_SELF_HEAL_ATTEMPTS = 3
_LOGIC_CLUSTER_COUNTS: dict[str, int] = {}
_LOGIC_ESCALATED: set[str] = set()


def classify_failure(error_message: str) -> str:
    msg = (error_message or "").lower()
    for failure_class, patterns in FAILURE_CLASSES.items():
        if any(p in msg for p in patterns):
            return failure_class
    return "UNKNOWN"


def retry_after(seconds: int) -> None:
    logger.warning("FLAKE failure detected. Retrying after %s seconds.", seconds)
    time.sleep(seconds)


def alert_human(room: str, error_message: str) -> None:
    logger.critical("INFRA failure detected: %s", error_message)
    try:
        room_id = room.replace("#", "%23").replace(":", "%3A")
        url = f"http://tuwunel-matrix:8008/_matrix/client/v3/rooms/{room_id}/send/m.room.message/{uuid.uuid4()}"
        httpx.put(url, json={"msgtype": "m.text", "body": f"🚨 URGENT INFRA FAILURE: {error_message}"}, timeout=2.0)
    except Exception as e:
        logger.error("Failed to alert human on Matrix: %s", e)


def _enqueue_dead_letter(error_message: str, attempts: int) -> None:
    payload = {
        "task": "Dead-letter LOGIC failure",
        "reason": error_message,
        "attempts": attempts,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    try:
        httpx.post("http://localhost:8000/api/v1/dead-letter", json=payload, timeout=2.0)
    except Exception as e:
        logger.error("Failed to enqueue dead-letter item: %s", e)


def _root_signature(error_message: str) -> str:
    normalized = " ".join((error_message or "").lower().split())
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


def enter_self_healing_loop(error_message: str, attempts: int = 1) -> None:
    logger.info("LOGIC failure detected. Self-heal attempt %s for: %s", attempts, error_message)
    if attempts > MAX_SELF_HEAL_ATTEMPTS:
        _enqueue_dead_letter(error_message, attempts)
        alert_human("#daemon-ops:daemon.local", f"Dead-lettered LOGIC failure after {attempts} attempts: {error_message}")
        return

    try:
        httpx.post(
            "http://localhost:8000/api/v1/jobs",
            json={"task": f"Self-heal failure: {error_message}", "attempts": attempts},
            timeout=2.0,
        )
    except Exception as e:
        logger.error("Failed to trigger self-healing job: %s", e)


def _extract_attempts(error_message: str) -> int:
    marker = "attempt="
    if marker not in error_message:
        return 1
    try:
        tail = error_message.split(marker, 1)[1]
        return int(tail.split()[0])
    except Exception:
        return 1


def handle_failure(error_message: str, *, max_self_heal_attempts: int = MAX_SELF_HEAL_ATTEMPTS) -> None:
    cls = classify_failure(error_message)
    if cls == "FLAKE":
        retry_after(120)
        return

    if cls in ["INFRA", "UNKNOWN"]:
        alert_human("#daemon-ops:daemon.local", error_message)
        return

    sig = _root_signature(error_message)
    _LOGIC_CLUSTER_COUNTS[sig] = _LOGIC_CLUSTER_COUNTS.get(sig, 0) + 1
    attempts = max(_extract_attempts(error_message), _LOGIC_CLUSTER_COUNTS[sig]) + 1

    if _LOGIC_CLUSTER_COUNTS[sig] <= max_self_heal_attempts:
        enter_self_healing_loop(error_message)
        return

    if sig not in _LOGIC_ESCALATED:
        _enqueue_dead_letter(error_message, attempts)
        alert_human("#daemon-ops:daemon.local", f"Repeated LOGIC failure cluster={sig}: {error_message}")
        _LOGIC_ESCALATED.add(sig)


def classify_failure_with_context(error_message: str, openhuman_context: dict[str, Any] | None = None) -> str:
    cls = classify_failure(error_message)
    if openhuman_context and openhuman_context.get("openhuman_status") == "degraded" and cls == "UNKNOWN":
        return "FLAKE"
    return cls
