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

    def process_task(self, task: str):
        """Processes a single task through the entire agency lifecycle."""
        logger.info(f"--- Starting new task: {task} ---")

        # 1. Retrieve prior context
        past_lessons = agent_memory.retrieve_lessons(task)
        if past_lessons != "No past lessons found.":
            logger.info("Applying prior lessons to this task.")

        # 2. Plan
        plan_prompt = f"Task: {task}\nPrior Context: {past_lessons}\nCreate a structured implementation plan."
        plan = self.planner.create_plan(plan_prompt)
        logger.info(f"Plan generated.")

        # 3. Execute
        code = self.engineer.write_code(plan)
        logger.info(f"Code generated.")

        # 4. Review
        review = self.reviewer.review_code(code)
        logger.info(f"Review completed.")

        # 5. Store outcome in long-term memory
        agent_memory.store_outcome(task, code, review)
        logger.info("Task completed and memorized.\n")
        return plan, code, review

    def run_worker_loop(self, task_queue: List[str]):
        """Runs the autonomous 24x7 loop processing a queue of tasks."""
        logger.info("Starting autonomous worker loop...")

        for idx, task in enumerate(task_queue):
            try:
                self.process_task(task)
                # Sleep briefly to avoid slamming the API too hard
                # In production 24x7, we'd poll a database or message queue here
                time.sleep(2)
            except Exception as e:
                logger.error(f"Error processing task '{task}': {e}")

        logger.info("Worker loop finished processing current queue.")

if __name__ == "__main__":
    mock_tasks = [
        "Write a Python function to parse a JSON configuration file and return a dictionary.",
        "Refactor a provided Python script that sorts a list of dictionaries by a specific key to use list comprehensions.",
        "Create a small README.md file template for a standard Python CLI project."
    ]

    worker = OmniAgentWorker()
    worker.run_worker_loop(mock_tasks)
