from src.domain.agents.planner import PlannerAgent
from src.domain.agents.engineer import EngineerAgent
from src.domain.agents.reviewer import ReviewerAgent, ReviewStatus

class OmniAgentWorker:
    def __init__(self):
        self.planner = PlannerAgent()
        self.engineer = EngineerAgent()
        self.reviewer = ReviewerAgent()
        self.max_iterations = 2  # Limit for Hermes-style self-evolution loop

    def process_task(self, task: str):
        """Processes a single task through the entire agency lifecycle with self-evolution."""
        plan = self.planner.create_plan(task)
        code = self.engineer.write_code(plan)

        for i in range(self.max_iterations):
            review = self.reviewer.review_code(code)
            if review.status in [ReviewStatus.PASS, ReviewStatus.PASS_WITH_NOTES]:
                break
            if i < self.max_iterations - 1:
                code = self.engineer.iterate_code(code, review.feedback)

        return plan, code, review.feedback
