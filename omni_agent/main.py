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
        self.max_iterations = 3  # Limit for Hermes-style self-evolution loop

    def process_task(self, task: str):
        """Processes a single task through the entire agency lifecycle with deep self-evolution."""
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

        # 4. Deep Review & Self-Evolution Loop (Hermes pattern)
        final_review = "APPROVED"
        for i in range(self.max_iterations):
            review = self.reviewer.review_code(code)
            logger.info(f"Review cycle {i+1} completed.")

            # Simple check for approval vs feedback
            if "APPROVED" in review and i > 0:
                final_review = review
                break
            elif "APPROVED" in review:
                # If mock approves instantly, simulate strict feedback
                review = "[MOCK RESPONSE] Ensure the code structure is highly scalable and handles edge cases."

            logger.info("Feedback received. Iterating code...")
            code = self.engineer.iterate_code(code, review)
            final_review = review

        # 5. Meta-Reflection (Continuous improvement)
        logger.info("Extracting meta-lessons from execution...")
        reflection = self.reviewer.reflect(code, final_review)

        # 6. Store generalized outcome in long-term memory
        agent_memory.store_outcome(task, code, f"Specific Feedback: {final_review}\nMeta-Lesson: {reflection}")
        logger.info("Task completed, evolved, reflected upon, and memorized.\n")
        return plan, code, final_review

    def run_worker_loop(self, task_queue: List[str]):
        """Runs the autonomous 24x7 loop processing a queue of tasks."""
        logger.info("Starting Fully Autonomous Omni-Worker Loop (GStack/Hermes/Deerflow capabilities)...")

        for idx, task in enumerate(task_queue):
            try:
                self.process_task(task)
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error processing task '{task}': {e}")

        logger.info("Worker loop finished processing current queue.")

if __name__ == "__main__":
    # The queue can accept *any* generic benign task
    mock_tasks = [
        "Design and implement a highly concurrent web crawler in Python.",
        "Refactor an existing monolithic Python application into an event-driven microservices architecture blueprint."
    ]

    worker = OmniAgentWorker()
    worker.run_worker_loop(mock_tasks)
