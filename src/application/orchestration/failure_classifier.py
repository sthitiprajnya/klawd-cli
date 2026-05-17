import logging
import time
from src.application.workflows import workflow

logger = logging.getLogger("FailureClassifier")

FAILURE_CLASSES = {
    "FLAKE": ["connection reset by peer", "rate limit", "network unreachable"],
    "INFRA": ["no space left on device", "oom kill", "permission denied"],
    "LOGIC": ["assertionerror", "typeerror", "expected but got", "test_"]
}

def classify_failure(error_message: str) -> str:
    msg = error_message.lower()
    for failure_class, patterns in FAILURE_CLASSES.items():
        if any(p in msg for p in patterns): return failure_class
    return "UNKNOWN"

def handle_failure(error_message: str):
    cls = classify_failure(error_message)
    if cls == "FLAKE":
        logger.warning(f"FLAKE failure detected: {error_message}. Retrying...")
        time.sleep(120)
    elif cls in ["INFRA", "UNKNOWN"]:
        logger.critical(f"INFRA/UNKNOWN failure detected: {error_message}. Alerting #daemon-ops.")
    elif cls == "LOGIC":
        logger.info(f"LOGIC failure detected: {error_message}. Entering self-healing loop.")
        workflow.process_task(f"Self-heal failure: {error_message}")