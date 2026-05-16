from .base import BaseAgent

ENGINEER_PROMPT = """You are the Senior Software Engineer (GStack level).
Your job is to execute technical plans and write high-quality, efficient, and benign code.
Ensure code follows best practices. Do not include any malicious or offensive security tools.
You are capable of deep reasoning and complex algorithms.
Output clean code with minimal commentary. If provided with feedback, iteratively improve the code."""

class EngineerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Bob", role="Engineer", system_prompt=ENGINEER_PROMPT)

    def write_code(self, task: str) -> str:
        return self.process(task, task_type="coding")

    def iterate_code(self, original_code: str, feedback: str) -> str:
        prompt = f"Original Code:\n{original_code}\n\nReviewer Feedback:\n{feedback}\n\nPlease revise the code to address the feedback."
        return self.process(prompt, task_type="coding")
