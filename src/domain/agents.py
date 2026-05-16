import logging
from abc import ABC
from src.infrastructure.llm_router import llm_router

logger = logging.getLogger("Agents")

class BaseAgent(ABC):
    def __init__(self, name: str, role: str, system_prompt: str):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt

    def process(self, prompt: str, task_type: str = "coding") -> str:
        logger.info(f"{self.name} processing task.")
        full_prompt = f"System: {self.system_prompt}\n\nUser: {prompt}"
        return llm_router.route(full_prompt, task_type=task_type)

    def reflect(self, outcome: str, feedback: str) -> str:
        prompt = f"Extract reusable lessons from:\nOutcome: {outcome}\nFeedback: {feedback}"
        return self.process(prompt, task_type="reflection")

class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__("Alice", "Planner", "You are the Lead Planner. Break tasks into execution pipelines. Benign tasks only.")
    def create_plan(self, request: str) -> str:
        return self.process(request, task_type="fast")

class EngineerAgent(BaseAgent):
    def __init__(self):
        super().__init__("Bob", "Engineer", "You are the Senior Engineer. Write clean, benign code.")
    def write_code(self, task: str) -> str:
        return self.process(task, task_type="coding")
    def iterate_code(self, code: str, feedback: str) -> str:
        return self.process(f"Code:\n{code}\nFeedback:\n{feedback}\nRevise code.", task_type="coding")

class ReviewerAgent(BaseAgent):
    def __init__(self):
        super().__init__("Charlie", "Reviewer", "You are the QA Reviewer. Provide feedback for self-evolution or output 'APPROVED'.")
    def review_code(self, code: str) -> str:
        return self.process(code, task_type="complex")

class AbsorberAgent(BaseAgent):
    def __init__(self):
        super().__init__("Buu", "Absorber", "Abstract core benign functionality from repos into python modules.")
    def absorb_repo(self, repo_info: str) -> str:
        return self.process(f"Absorb: {repo_info}", task_type="complex")
