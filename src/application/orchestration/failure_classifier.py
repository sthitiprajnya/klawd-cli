import json
import logging
import time
import uuid
from datetime import datetime, timezone

import httpx

logger = logging.getLogger("FailureClassifier")

FAILURE_CLASSES = {
    "FLAKE": ["connection reset by peer", "rate limit", "network unreachable"],
    "INFRA": ["no space left on device", "oom kill", "permission denied"],
    "LOGIC": ["assertionerror", "typeerror", "expected but got", "test_"],
}

MAX_SELF_HEAL_ATTEMPTS = 3


def classify_failure(error_message: str) -> str:
    msg = error_message.lower()
    for failure_class, patterns in FAILURE_CLASSES.items():
        if any(p in msg for p in patterns):
            return failure_class
    return "UNKNOWN"


def retry_after(seconds: int):
    logger.warning("FLAKE failure detected. Retrying after %s seconds.", seconds)
    time.sleep(seconds)


def alert_human(room: str, error_message: str):
    logger.critical("INFRA failure detected: %s", error_message)
    try:
        room_id = room.replace("#", "%23").replace(":", "%3A")
        url = f"http://tuwunel-matrix:8008/_matrix/client/v3/rooms/{room_id}/send/m.room.message/{uuid.uuid4()}"
        httpx.put(url, json={"msgtype": "m.text", "body": f"🚨 URGENT INFRA FAILURE: {error_message}"})
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


def enter_self_healing_loop(error_message: str, attempts: int = 1):
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
    """Extract attempt marker from error text if present, defaulting to 1."""
    marker = "attempt="
    if marker not in error_message:
        return 1
    try:
        tail = error_message.split(marker, 1)[1]
        return int(tail.split()[0])
    except Exception:
        return 1


def handle_failure(error_message: str):
    cls = classify_failure(error_message)
    if cls == "FLAKE":
        retry_after(120)
    elif cls in ["INFRA", "UNKNOWN"]:
        alert_human("#daemon-ops:daemon.local", error_message)
    elif cls == "LOGIC":
        attempts = _extract_attempts(error_message)
        enter_self_healing_loop(error_message, attempts=attempts + 1)
