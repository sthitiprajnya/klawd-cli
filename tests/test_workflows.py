from unittest.mock import MagicMock

from src.application.workflows import OmniWorkflow
from src.domain.agents.reviewer import ReviewResult, ReviewStatus


def _mk_review(status: ReviewStatus, feedback: str) -> ReviewResult:
    return ReviewResult(status=status, feedback=feedback)


def test_workflow_pass_first_try():
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
    wf.engineer.iterate_code.assert_not_called()


def test_workflow_retry_then_pass_with_notes():
    wf = OmniWorkflow()
    wf.max_iterations = 3
    wf.planner.create_plan = MagicMock(return_value="plan")
    wf.engineer.write_code = MagicMock(return_value="bad")
    wf.engineer.iterate_code = MagicMock(return_value="better")
    wf.reviewer.review_code = MagicMock(side_effect=[
        _mk_review(ReviewStatus.FAIL_WITH_FEEDBACK, "FAIL_WITH_FEEDBACK\nFix issue"),
        _mk_review(ReviewStatus.PASS_WITH_NOTES, "PASS_WITH_NOTES\nMinor note"),
    ])
    wf.reviewer.reflect = MagicMock(return_value="reflection")
    wf._run_static_review_hooks = MagicMock(return_value=[])

    _, _, review = wf.process_task("do thing")

    assert "PASS_WITH_NOTES" in review
    assert wf.engineer.iterate_code.call_count == 1


def test_workflow_fail_all_retries():
    wf = OmniWorkflow()
    wf.max_iterations = 2
    wf.planner.create_plan = MagicMock(return_value="plan")
    wf.engineer.write_code = MagicMock(return_value="bad")
    wf.engineer.iterate_code = MagicMock(return_value="still bad")
    wf.reviewer.review_code = MagicMock(return_value=_mk_review(ReviewStatus.FAIL_WITH_FEEDBACK, "FAIL_WITH_FEEDBACK\nFix issue"))
    wf.reviewer.reflect = MagicMock(return_value="reflection")
    wf._run_static_review_hooks = MagicMock(return_value=[])

    _, _, review = wf.process_task("do thing")

    assert "FAIL_WITH_FEEDBACK" in review
    assert wf.engineer.iterate_code.call_count == 2
