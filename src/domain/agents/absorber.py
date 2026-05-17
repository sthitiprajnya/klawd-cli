from .base import BaseAgent

ABSORBER_PROMPT = "Abstract core benign functionality from repos into python modules."

class AbsorberAgent(BaseAgent):
    def __init__(self):
        super().__init__("Buu", "Absorber", ABSORBER_PROMPT)

    def absorb_repo(self, repo_info: str) -> str:
        return self.process(f"Absorb: {repo_info}", task_type="complex")
