from .base import BaseAgent

PLANNER_PROMPT = """You are the Lead Technical Planner (CEO/PM role).
Your job is to take a high-level request and break it down into an advanced Directed Acyclic Graph (DAG) or robust workflow pipeline.
Focus purely on benign, constructive software engineering tasks.
Identify dependencies between tasks and outline an execution sequence.
Output a clear, step-by-step pipeline execution plan."""

class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Alice", role="Planner", system_prompt=PLANNER_PROMPT)

    def create_plan(self, request: str, openhuman_context: dict | None = None) -> str:
        if openhuman_context:
            request = f"{request}\n\nOpenHuman Context: {openhuman_context}"
        return self.process(request, task_type="fast", openhuman_context=openhuman_context)
