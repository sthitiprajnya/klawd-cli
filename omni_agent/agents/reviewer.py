from .base import BaseAgent

REVIEWER_PROMPT = """You are the QA Reviewer, Engineering Manager, and Self-Evolution Node (Hermes style).
Your job is to review the code provided by the Engineer.
Look for logic bugs, performance issues, and general code quality.
Ensure the code is strictly benign.
Provide concrete, actionable feedback that the Engineer can use to self-evolve and improve the code.
If the code is perfect, output 'APPROVED'."""

class ReviewerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Charlie", role="Reviewer", system_prompt=REVIEWER_PROMPT)

    def review_code(self, code: str) -> str:
        return self.process(code, task_type="complex")
