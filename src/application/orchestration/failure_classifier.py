import time
import logging
import httpx
import uuid

logger = logging.getLogger("FailureClassifier")

FAILURE_CLASSES = {
    "FLAKE": ["connection reset by peer", "rate limit", "network unreachable"],
    "INFRA": ["no space left on device", "oom kill", "permission denied"],
    "LOGIC": ["assertionerror", "typeerror", "expected but got", "test_"]
}

def classify_failure(error_message: str) -> str:
    msg = error_message.lower()
    for failure_class, patterns in FAILURE_CLASSES.items():
        if any(p in msg for p in patterns):
            return failure_class
    return "UNKNOWN"

def retry_after(seconds: int):
    logger.warning(f"FLAKE failure detected. Retrying after {seconds} seconds.")
    time.sleep(seconds)

def alert_human(room: str, error_message: str):
    logger.critical(f"INFRA failure detected: {error_message}")
    try:
        room_id = room.replace("#", "%23").replace(":", "%3A")
        url = f"http://tuwunel-matrix:8008/_matrix/client/v3/rooms/{room_id}/send/m.room.message/{uuid.uuid4()}"
        httpx.put(url, json={"msgtype": "m.text", "body": f"🚨 URGENT INFRA FAILURE: {error_message}"})
    except Exception as e:
        logger.error(f"Failed to alert human on Matrix: {e}")

def enter_self_healing_loop(error_message: str):
    logger.info(f"LOGIC failure detected. Entering self-healing loop for: {error_message}")
    try:
        httpx.post("http://localhost:8000/api/v1/jobs", json={"task": f"Self-heal failure: {error_message}"})
    except Exception as e:
        logger.error(f"Failed to trigger self-healing job: {e}")

def handle_failure(error_message: str):
    cls = classify_failure(error_message)
    if cls == "FLAKE":
        retry_after(120)
    elif cls in ["INFRA", "UNKNOWN"]:
        alert_human("#daemon-ops:daemon.local", error_message)
    elif cls == "LOGIC":
        enter_self_healing_loop(error_message)


def classify_failure_with_context(error_message: str, openhuman_context: dict[str, object] | None = None) -> str:
    cls = classify_failure(error_message)
    if openhuman_context and openhuman_context.get("openhuman_status") == "degraded" and cls == "UNKNOWN":
        return "FLAKE"
    return cls
