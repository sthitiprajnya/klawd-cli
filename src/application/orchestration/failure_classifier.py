import time
import logging
from src.infrastructure.registry.skill_registry import MatrixClient

logger = logging.getLogger("FailureClassifier")
matrix = MatrixClient()

FAILURE_CLASSES = {
    "FLAKE": ["connection reset by peer", "rate limit", "network unreachable", "timeout"],
    "INFRA": ["no space left on device", "oom kill", "permission denied", "docker: cannot connect"],
    "LOGIC": ["assertionerror", "typeerror", "expected but got", "test_"]
}

def classify_failure(error_message: str) -> str:
    msg = error_message.lower()
    for failure_class, patterns in FAILURE_CLASSES.items():
        if any(p in msg for p in patterns):
            return failure_class
    return "UNKNOWN"

def retry_after(seconds: int):
    logger.info(f"FLAKE detected. Retrying after {seconds} seconds.")
    time.sleep(seconds)

def alert_human(room: str, msg: str):
    logger.error(f"INFRA failure escalated to human in {room}.")
    matrix.send_to_room(room, f"🚨 URGENT: Infrastructure failure requires human intervention. Details: {msg}")

def enter_self_healing_loop():
    logger.info("LOGIC failure detected. Entering DSPy self-healing loop.")
    matrix.send_to_room("#daemon-ops:daemon.local", "Initiating DSPy self-healing loop for logic failure.")
    # In a full run, this would invoke the hermes-agent-self-evolution CLI or API

def handle_failure(error_message: str):
    cls = classify_failure(error_message)
    if cls == "FLAKE":
        retry_after(120)
    elif cls in ["INFRA", "UNKNOWN"]:
        alert_human("#daemon-ops:daemon.local", error_message)
    elif cls == "LOGIC":
        enter_self_healing_loop()
