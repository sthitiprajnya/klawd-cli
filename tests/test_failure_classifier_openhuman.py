from src.application.orchestration.failure_classifier import classify_failure_with_context


def test_degraded_unknown_promotes_to_flake():
    assert classify_failure_with_context("mystery", {"openhuman_status": "degraded"}) == "FLAKE"


def test_non_degraded_unknown_remains_unknown():
    assert classify_failure_with_context("mystery", {"openhuman_status": "available"}) == "UNKNOWN"
