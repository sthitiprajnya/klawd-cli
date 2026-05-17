import logging
import httpx
import os
from abc import ABC
from src.infrastructure.llm_router import llm_router

logger = logging.getLogger("Agents")

class BaseAgent(ABC):
    def __init__(self, name: str, role: str, system_prompt: str):
        self.name = name
        self.role = role
        self.base_system_prompt = system_prompt
        self.openhuman_url = "http://openhuman-core:7788/rpc" # Real OpenHuman headless endpoint
        self.token = os.getenv("OPENHUMAN_CORE_TOKEN", "dummy-token")

    def _get_dynamic_context(self) -> str:
        """Fetches dynamic global context from OpenHuman memory trees."""
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "openhuman.memory_tree_ingest",
                "params": {},
                "id": 1
            }
            response = httpx.post(
                self.openhuman_url,
                json=payload,
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=2.0
            )
            if response.status_code == 200:
                data = response.json()
                if "result" in data and data["result"]:
                    return f"\n[Dynamic Global Context from OpenHuman: {data['result']}]"
        except Exception as e:
            logger.debug(f"Failed to fetch dynamic context from OpenHuman: {e}")
        return ""

    def process(self, prompt: str, task_type: str = "coding") -> str:
        logger.info(f"{self.name} ({self.role}) is processing task.")
        dynamic_context = self._get_dynamic_context()
        full_system_prompt = f"{self.base_system_prompt}{dynamic_context}"
        full_prompt = f"System: {full_system_prompt}\n\nUser: {prompt}"
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
