import time
import logging
from typing import List

from omni_agent.agents import PlannerAgent, EngineerAgent, ReviewerAgent
from omni_agent.utils.memory import agent_memory

# Setup basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("WorkerLoop")

class OmniAgentWorker:
    def __init__(self):
        self.planner = PlannerAgent()
        self.engineer = EngineerAgent()
        self.reviewer = ReviewerAgent()
        self.max_iterations = 2  # Limit for Hermes-style self-evolution loop

    def process_task(self, task: str):
        """Processes a single task through the entire agency lifecycle with self-evolution."""
        logger.info(f"--- Starting new task: {task} ---")

        # 1. Retrieve prior context (MemPalace pattern)
        past_lessons = agent_memory.retrieve_lessons(task)
        if past_lessons != "No past lessons found.":
            logger.info("Applying prior lessons to this task.")

        # 2. Plan (Deerflow DAG orchestration pattern)
        plan_prompt = f"Task: {task}\nPrior Context: {past_lessons}\nCreate a structured implementation pipeline."
        plan = self.planner.create_plan(plan_prompt)
        logger.info(f"Pipeline Plan generated.")

        # 3. Initial Execution
        code = self.engineer.write_code(plan)
        logger.info(f"Initial Code generated.")

        # 4. Review & Self-Evolution Loop (Hermes pattern)
        final_review = "APPROVED"
        for i in range(self.max_iterations):
            review = self.reviewer.review_code(code)
            logger.info(f"Review cycle {i+1} completed.")

            # Simple check for approval vs feedback
            if "APPROVED" in review and i > 0: # Force at least one review cycle mock
                final_review = review
                break
            elif "APPROVED" in review:
                # If mock approves instantly, let's pretend it gave feedback for testing the loop
                review = "[MOCK RESPONSE] Needs optimization in loop structures."

            logger.info("Feedback received. Iterating code...")
            code = self.engineer.iterate_code(code, review)
            final_review = review

        # 5. Store outcome in long-term memory
        agent_memory.store_outcome(task, code, final_review)
        logger.info("Task completed, evolved, and memorized.\n")
        return plan, code, final_review

    def run_worker_loop(self, task_queue: List[str]):
        """Runs the autonomous 24x7 loop processing a queue of tasks."""
        logger.info("Starting autonomous worker loop (GStack/Hermes/Deerflow capabilities)...")

        for idx, task in enumerate(task_queue):
            try:
                self.process_task(task)
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error processing task '{task}': {e}")

        logger.info("Worker loop finished processing current queue.")

if __name__ == "__main__":
    mock_tasks = [
        "Build a robust HTTP caching layer in Python that supports Redis and local dict backends."
    ]

    worker = OmniAgentWorker()
    worker.run_worker_loop(mock_tasks)
