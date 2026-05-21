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
