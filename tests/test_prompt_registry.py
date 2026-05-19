from src.application.prompt_registry import PromptVersionRegistry


def test_promotion_success_when_threshold_met():
    events = []
    registry = PromptVersionRegistry(
        minimum_improvement_threshold=0.05,
        notifier=events.append,
        audit_logger=events.append,
    )
    registry.register_version("v1", base_score=0.50)

    promoted = registry.try_promote(
        candidate_version="v2",
        recent_job_outcomes=[{"status": "completed"}] * 8 + [{"status": "failed"}] * 2,
        reviewer_artifacts=[{"status": "pass", "static_findings": 1}] * 8 + [{"status": "fail", "static_findings": 4}] * 2,
        held_out_score=0.95,
    )

    assert promoted is True
    assert registry.active_version == "v2"
    assert registry.get_record("v2").promoted_at is not None
    assert any(e["event"] == "prompt_promoted" for e in events)


def test_promotion_rejected_when_threshold_not_met():
    events = []
    registry = PromptVersionRegistry(
        minimum_improvement_threshold=0.10,
        notifier=events.append,
        audit_logger=events.append,
    )
    registry.register_version("v1", base_score=0.80)

    promoted = registry.try_promote(
        candidate_version="v2",
        recent_job_outcomes=[{"status": "completed"}] * 7 + [{"status": "failed"}] * 3,
        reviewer_artifacts=[{"status": "pass", "static_findings": 2}] * 7 + [{"status": "fail", "static_findings": 3}] * 3,
        held_out_score=0.70,
    )

    assert promoted is False
    assert registry.active_version == "v1"
    assert any(e["event"] == "prompt_promotion_rejected" for e in events)


def test_rollback_marks_active_version_and_switches_target():
    events = []
    registry = PromptVersionRegistry(notifier=events.append, audit_logger=events.append)
    registry.register_version("v1", base_score=0.50)
    registry.register_version("v2", base_score=0.70)

    registry.try_promote(
        candidate_version="v2",
        recent_job_outcomes=[{"status": "completed"}] * 10,
        reviewer_artifacts=[{"status": "pass", "static_findings": 0}] * 10,
        held_out_score=1.0,
    )

    registry.rollback(to_version="v1", reason="regression observed")

    assert registry.active_version == "v1"
    assert registry.get_record("v2").rolled_back_at is not None
    assert any(e["event"] == "prompt_rolled_back" for e in events)
