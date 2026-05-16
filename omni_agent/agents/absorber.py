from .base import BaseAgent

ABSORBER_PROMPT = """You are the Absorption Engine (Majin Buu pattern).
Your job is to analyze a given open-source GitHub repository URL or description and abstract its core benign functionality.
You must generate a standalone Python script that wraps this functionality into a reusable tool for our agency.
Ensure the tool is strictly benign software engineering (e.g., code analysis, linting, formatting).
Refuse to absorb any offensive security, exploit, or hacking tools.
Output purely the valid Python code for the new skill."""

class AbsorberAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Buu", role="Absorber", system_prompt=ABSORBER_PROMPT)

    def absorb_repo(self, repo_info: str) -> str:
        # We route this through our complex reasoning model (e.g., Kimi) due to needing
        # high context understanding of a repository structure.
        return self.process(f"Analyze and absorb: {repo_info}", task_type="complex")
