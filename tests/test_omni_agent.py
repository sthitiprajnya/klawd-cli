import pytest
from unittest.mock import MagicMock
from omni_agent.main import OmniAgentWorker
from src.domain.agents.reviewer import ReviewResult, ReviewStatus

def _mk_review(status, feedback):
    return ReviewResult(status=status, feedback=feedback)

def test_process_task_success_first_try():
    worker = OmniAgentWorker()
    worker.planner.create_plan = MagicMock(return_value="test plan")
    worker.engineer.write_code = MagicMock(return_value="test code")
    worker.reviewer.review_code = MagicMock(return_value=_mk_review(ReviewStatus.PASS, "Looks good"))

    plan, code, feedback = worker.process_task("do test task")

    assert plan == "test plan"
    assert code == "test code"
    assert feedback == "Looks good"
    worker.planner.create_plan.assert_called_once_with("do test task")
    worker.engineer.write_code.assert_called_once_with("test plan")
    worker.reviewer.review_code.assert_called_once_with("test code")

def test_process_task_iteration_loop():
    worker = OmniAgentWorker()
    worker.planner.create_plan = MagicMock(return_value="test plan")
    worker.engineer.write_code = MagicMock(return_value="initial code")
    worker.engineer.iterate_code = MagicMock(return_value="fixed code")

    worker.reviewer.review_code = MagicMock(side_effect=[
        _mk_review(ReviewStatus.FAIL_WITH_FEEDBACK, "needs fix"),
        _mk_review(ReviewStatus.PASS, "all good")
    ])

    plan, code, feedback = worker.process_task("do test task")

    assert plan == "test plan"
    assert code == "fixed code"
    assert feedback == "all good"
    assert worker.reviewer.review_code.call_count == 2
    worker.engineer.iterate_code.assert_called_once_with("initial code", "needs fix")

def test_process_task_max_iterations():
    worker = OmniAgentWorker()
    worker.planner.create_plan = MagicMock(return_value="test plan")
    worker.engineer.write_code = MagicMock(return_value="code 1")
    worker.engineer.iterate_code = MagicMock(return_value="code 2")

    worker.reviewer.review_code = MagicMock(return_value=_mk_review(ReviewStatus.FAIL_WITH_FEEDBACK, "fail"))

    plan, code, feedback = worker.process_task("task")

    assert worker.reviewer.review_code.call_count == worker.max_iterations
    assert worker.engineer.iterate_code.call_count == worker.max_iterations - 1
