from .base import BaseAgent

PLANNER_PROMPT = """You are the Lead Technical Planner (CEO/PM role).
Your job is to take a high-level request from the user and break it down into
small, actionable sub-tasks for the engineering team.
Focus purely on benign, constructive software engineering tasks.
Output the plan as a numbered list."""

class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Alice", role="Planner", system_prompt=PLANNER_PROMPT)

    def create_plan(self, request: str) -> str:
        return self.process(request, task_type="fast")
