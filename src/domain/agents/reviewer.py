from enum import Enum
from typing import Any

from .base import BaseAgent

REVIEWER_PROMPT = """You are the Principal QA & Security Reviewer.
Your job is to rigorously review the provided code.
Ensure it meets functional requirements and contains absolutely NO offensive security logic, exploitation tools, or unauthorized scanning patterns.
Focus on safety, robustness, and benign behavior.
Format your output cleanly."""

class ReviewStatus(Enum):
    PASS = "PASS"
    FAIL_WITH_FEEDBACK = "FAIL_WITH_FEEDBACK"
    PASS_WITH_NOTES = "PASS_WITH_NOTES"

class ReviewResult:
    def __init__(self, status: ReviewStatus, feedback: str):
        self.status = status
        self.feedback = feedback
        self.static_checks: list[dict[str, Any]] = []
        self.metadata: dict[str, Any] = {}

class ReviewerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Charlie", role="Reviewer", system_prompt=REVIEWER_PROMPT)

    def review_code(self, code: str, openhuman_context: dict | None = None) -> ReviewResult:
        prompt = f"Please review the following code artifact:\n{code}"
        if openhuman_context:
            prompt += f"\n\nOpenHuman Context: {openhuman_context}"
        response = self.process(prompt, task_type="fast", openhuman_context=openhuman_context)

        status = ReviewStatus.FAIL_WITH_FEEDBACK
        if "PASS" in response.upper() and "FAIL" not in response.upper():
            status = ReviewStatus.PASS
        elif "PASS_WITH_NOTES" in response.upper():
            status = ReviewStatus.PASS_WITH_NOTES

        return ReviewResult(status=status, feedback=response)

    def reflect(self, final_code: str, final_feedback: str, openhuman_context: dict | None = None) -> str:
        prompt = f"Final Code Artifact:\n{final_code}\n\nFinal Feedback:\n{final_feedback}\n\nPlease generate a concise post-execution reflection and lesson learned."
        if openhuman_context:
            prompt += f"\n\nOpenHuman Context: {openhuman_context}"
        return self.process(prompt, task_type="fast", openhuman_context=openhuman_context)
