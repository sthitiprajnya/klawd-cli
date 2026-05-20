from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .base import BaseAgent

REVIEWER_PROMPT = """You are the QA Reviewer, Engineering Manager, and Self-Evolution Node (Hermes style).
Your job is to review the code provided by the Engineer.
Look for logic bugs, performance issues, and general code quality.
Ensure the code is strictly benign.
Provide concrete, actionable feedback that the Engineer can use to self-evolve and improve the code.
Return only one of these first-line status tags: PASS, PASS_WITH_NOTES, FAIL_WITH_FEEDBACK."""


class ReviewStatus(str, Enum):
    PASS = "PASS"
    PASS_WITH_NOTES = "PASS_WITH_NOTES"
    FAIL_WITH_FEEDBACK = "FAIL_WITH_FEEDBACK"


@dataclass
class ReviewResult:
    status: ReviewStatus
    feedback: str
    static_checks: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class ReviewerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Charlie", role="Reviewer", system_prompt=REVIEWER_PROMPT)

    def review_code(self, code: str, openhuman_context: dict | None = None) -> ReviewResult:
        prompt = code
        if openhuman_context:
            prompt = f"{code}\n\nOpenHuman Context: {openhuman_context}"
        review_text = self.process(prompt, task_type="complex").strip()
        first_line = review_text.splitlines()[0].strip() if review_text else ""

        if first_line.startswith(ReviewStatus.PASS.value):
            status = ReviewStatus.PASS
        elif first_line.startswith(ReviewStatus.PASS_WITH_NOTES.value):
            status = ReviewStatus.PASS_WITH_NOTES
        else:
            status = ReviewStatus.FAIL_WITH_FEEDBACK

        return ReviewResult(status=status, feedback=review_text)

    def reflect(self, code: str, feedback: str, openhuman_context: dict | None = None) -> str:
        prompt = f"Reflect on this review.\nCode:\n{code}\n\nFeedback:\n{feedback}"
        if openhuman_context:
            prompt += f"\n\nOpenHuman Context: {openhuman_context}"
        return self.process(prompt, task_type="fast")
