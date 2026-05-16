# --- Mocks ---
def retry_after(s): pass
def alert_human(room): pass
def enter_self_healing_loop(): pass
# -------------

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
    if cls == "FLAKE": retry_after(120)
    elif cls in ["INFRA", "UNKNOWN"]: alert_human("#daemon-ops")
    elif cls == "LOGIC": enter_self_healing_loop()