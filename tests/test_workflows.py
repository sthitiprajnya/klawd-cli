from unittest.mock import MagicMock

from src.application.workflows import OmniWorkflow
from src.domain.agents.reviewer import ReviewResult, ReviewStatus


def _mk_review(status: ReviewStatus, feedback: str) -> ReviewResult:
    return ReviewResult(status=status, feedback=feedback)


def test_openhuman_context_propagates_through_stages():
    wf = OmniWorkflow()
    wf.planner.create_plan = MagicMock(return_value="plan")
    wf.engineer.write_code = MagicMock(return_value="print(1)")
    wf.reviewer.review_code = MagicMock(return_value=_mk_review(ReviewStatus.PASS, "PASS\nLooks good"))
    wf.reviewer.reflect = MagicMock(return_value="reflection")
    wf._run_static_review_hooks = MagicMock(return_value=[])

    plan, code, review = wf.process_task("do thing")

    assert plan == "plan"
    assert code == "print(1)"
    assert "PASS" in review
    assert "openhuman_context" in wf.reviewer.reflect.call_args.kwargs
    assert "openhuman_context" in wf.planner.create_plan.call_args.kwargs


def test_degraded_mode_timeout_marks_status():
    wf = OmniWorkflow()
    wf.planner.last_openhuman_observability = {"openhuman_available": False, "openhuman_error": "timeout"}
    wf.planner.create_plan = MagicMock(return_value="plan")
    wf.engineer.write_code = MagicMock(return_value="print(1)")
    wf.reviewer.review_code = MagicMock(return_value=_mk_review(ReviewStatus.PASS, "PASS\nLooks good"))
    wf.reviewer.reflect = MagicMock(return_value="reflection")
    wf._run_static_review_hooks = MagicMock(return_value=[])

    wf.process_task("do thing")

    ctx = wf.planner.create_plan.call_args.kwargs["openhuman_context"]
    assert ctx["openhuman_status"] == "degraded"


def test_audit_disabled_preserves_default_flow():
    wf = OmniWorkflow()
    wf.planner.create_plan = MagicMock(return_value="plan")
    wf.engineer.write_code = MagicMock(return_value="print(1)")
    wf.reviewer.review_code = MagicMock(return_value=_mk_review(ReviewStatus.PASS, "PASS\nLooks good"))
    wf.reviewer.reflect = MagicMock(return_value="reflection")
    wf._run_static_review_hooks = MagicMock(return_value=[])
    wf.auditor.audit_codebase = MagicMock(return_value="audit")

    _, _, feedback = wf.process_task("do thing")

    wf.auditor.audit_codebase.assert_not_called()
    assert "Auditor Findings" not in feedback


def test_audit_enabled_merges_findings_and_telemetry():
    wf = OmniWorkflow()
    wf.planner.create_plan = MagicMock(return_value="plan")
    wf.engineer.write_code = MagicMock(return_value="print(1)")
    wf.reviewer.review_code = MagicMock(return_value=_mk_review(ReviewStatus.PASS, "PASS\nLooks good"))
    wf.reviewer.reflect = MagicMock(return_value="reflection")
    wf._run_static_review_hooks = MagicMock(return_value=[])
    wf.auditor.audit_codebase = MagicMock(return_value="No critical issues")
    wf._run_cyberstrike_bolt_checks = MagicMock(return_value=[{"tool": "cyberstrike-bolt", "status": "ok", "rule": "benign-config"}])
    wf._run_hexstrike_recon = MagicMock(return_value={"enabled": True, "findings": [{"asset": "repo"}]})

    _, _, feedback = wf.process_task("do thing", audit_requested=True, audit_context={"run_recon": True, "recon_target": "repo"})

    wf.auditor.audit_codebase.assert_called_once()
    assert "Auditor Findings" in feedback
    assert "No critical issues" in feedback
