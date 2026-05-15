from .base import BaseAgent

REVIEWER_PROMPT = """You are the QA Reviewer and Engineering Manager.
Your job is to review the code provided by the Engineer.
Look for logic bugs, performance issues, and general code quality.
Ensure the code is strictly benign and does not contain any security exploitation tools.
Provide constructive feedback or approve the code."""

class ReviewerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Charlie", role="Reviewer", system_prompt=REVIEWER_PROMPT)

    def review_code(self, code: str) -> str:
        return self.process(code, task_type="complex")
