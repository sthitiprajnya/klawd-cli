from src.application.hermes.learning_loop import HermesLearningCoordinator
from src.application.prompt_registry import EvalInputContract, PromptVersionRegistry
from src.application.orchestration import failure_classifier


def test_duplicate_outcome_suppression():
    events = []
    registry = PromptVersionRegistry(audit_logger=events.append, notifier=events.append)
    registry.register_version("v1", 0.4)
    coordinator = HermesLearningCoordinator(registry=registry, audit_logger=events.append)
    outcomes = [{"id": "o1", "job_id": "j1", "root_signature": "r1"}]
    c1 = coordinator.build_candidate_from_outcomes(workflow_outcomes=outcomes, model_metadata={"provider": "x"}, reviewer_verdict="pass")
    c2 = coordinator.build_candidate_from_outcomes(workflow_outcomes=outcomes, model_metadata={"provider": "x"}, reviewer_verdict="pass")
    assert c1 is not None
    assert c2 is None


def test_bounded_self_heal_attempts(monkeypatch):
    failure_classifier._LOGIC_CLUSTER_COUNTS.clear()
    failure_classifier._LOGIC_ESCALATED.clear()
    healed = []
    escalated = []
    monkeypatch.setattr(failure_classifier, "enter_self_healing_loop", lambda msg, attempts: healed.append(msg))
    monkeypatch.setattr(failure_classifier, "alert_human", lambda room, msg: escalated.append((room, msg)))

    for _ in range(5):
        failure_classifier.handle_failure("AssertionError: expected but got 1")

    assert len(healed) == 3
    assert len(escalated) == 1


def test_promotion_rejected_when_contamination_metadata_missing():
    events = []
    registry = PromptVersionRegistry(minimum_improvement_threshold=0.01, audit_logger=events.append, notifier=events.append)
    registry.register_version("v1", 0.2)
    promoted = registry.try_promote(
        candidate_version="v2",
        recent_job_outcomes=[{"status": "completed"}] * 10,
        reviewer_artifacts=[{"status": "pass", "static_findings": 0}] * 10,
        held_out_score=0.9,
        eval_input=EvalInputContract(dataset_version="d1", evaluation_run_id="e1", contamination_window_end=""),
        safety_metrics={"toxicity": 0.98},
        baseline_safety_metrics={"toxicity": 0.95},
        retry_budget_remaining=1,
    )
    assert promoted is False
    assert any(e["event"] == "prompt_promotion_rejected" for e in events)
