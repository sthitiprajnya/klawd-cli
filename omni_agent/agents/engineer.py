from .base import BaseAgent

ENGINEER_PROMPT = """You are the Senior Software Engineer.
Your job is to execute technical plans and write high-quality, efficient, and benign code.
Ensure code follows best practices. Do not include any malicious or offensive security tools.
Output clean code with minimal commentary."""

class EngineerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Bob", role="Engineer", system_prompt=ENGINEER_PROMPT)

    def write_code(self, task: str) -> str:
        return self.process(task, task_type="coding")
