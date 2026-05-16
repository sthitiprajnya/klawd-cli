import time
import logging
import os
import re
from typing import List

from omni_agent.agents import PlannerAgent, EngineerAgent, ReviewerAgent, AbsorberAgent
from omni_agent.utils.memory import agent_memory
from omni_agent.utils.skill_manager import skill_manager

# Setup basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("WorkerLoop")

class OmniAgentWorker:
    def __init__(self):
        self.planner = PlannerAgent()
        self.engineer = EngineerAgent()
        self.reviewer = ReviewerAgent()
        self.absorber = AbsorberAgent()
        self.max_iterations = 3

    def _extract_code_block(self, text: str) -> str:
        """Utility to extract pure python code from markdown response."""
        match = re.search(r"```python\n(.*?)\n```", text, re.DOTALL)
        if match:
            return match.group(1)
        return text

    def process_absorption(self, task: str):
        """Special workflow for the Majin Buu absorption pattern."""
        logger.info("--- Starting Absorption Protocol ---")

        # 1. Absorb the feature
        logger.info("Absorbing repository features...")
        raw_skill_code = self.absorber.absorb_repo(task)
        clean_code = self._extract_code_block(raw_skill_code)

        # Determine a filename (mock implementation logic for filename generation)
        # In a real scenario, the LLM would output the intended filename or we'd extract it.
        skill_name = "absorbed_feature_" + str(int(time.time()))
        filepath = os.path.join("omni_agent", "skills", f"{skill_name}.py")

        # 2. Write and register the skill
        with open(filepath, "w") as f:
            f.write(clean_code)

        logger.info(f"Feature absorbed and written to {filepath}")

        # 3. Load into active memory
        skill_manager.load_skill(skill_name)

        # 4. Store memory so agents know they have it
        memory_entry = f"Successfully absorbed capability from {task}. Registered as {skill_name}."
        agent_memory.store_outcome("Absorption Protocol", clean_code, memory_entry)
        logger.info(f"Agent self-evolution complete. Now possesses {skill_name}.\n")

    def process_task(self, task: str):
        """Processes a single task through the entire agency lifecycle with deep self-evolution."""

        if "github.com" in task.lower() or "absorb" in task.lower():
            self.process_absorption(task)
            return

        logger.info(f"--- Starting new task: {task} ---")

        # Let agents know what custom skills they currently possess
        active_skills = skill_manager.list_skills()
        skill_context = f"\nCurrently Absorbed Skills available: {active_skills}" if active_skills else ""

        # 1. Retrieve prior context
        past_lessons = agent_memory.retrieve_lessons(task)
        if past_lessons != "No past lessons found.":
            logger.info("Applying prior lessons to this task.")

        # 2. Plan
        plan_prompt = f"Task: {task}\nPrior Context: {past_lessons}{skill_context}\nCreate a structured implementation pipeline."
        plan = self.planner.create_plan(plan_prompt)
        logger.info(f"Pipeline Plan generated.")

        # 3. Initial Execution
        code = self.engineer.write_code(plan)
        logger.info(f"Initial Code generated.")

        # 4. Deep Review & Self-Evolution Loop
        final_review = "APPROVED"
        for i in range(self.max_iterations):
            review = self.reviewer.review_code(code)
            logger.info(f"Review cycle {i+1} completed.")

            if "APPROVED" in review and i > 0:
                final_review = review
                break
            elif "APPROVED" in review:
                review = "[MOCK RESPONSE] Ensure the code structure is highly scalable and handles edge cases."

            logger.info("Feedback received. Iterating code...")
            code = self.engineer.iterate_code(code, review)
            final_review = review

        # 5. Meta-Reflection
        logger.info("Extracting meta-lessons from execution...")
        reflection = self.reviewer.reflect(code, final_review)

        # 6. Store generalized outcome
        agent_memory.store_outcome(task, code, f"Specific Feedback: {final_review}\nMeta-Lesson: {reflection}")
        logger.info("Task completed, evolved, reflected upon, and memorized.\n")

    def run_worker_loop(self, task_queue: List[str]):
        """Runs the autonomous 24x7 loop processing a queue of tasks."""
        logger.info("Starting Fully Autonomous Omni-Worker Loop with Absorption...")

        for idx, task in enumerate(task_queue):
            try:
                self.process_task(task)
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error processing task '{task}': {e}")

        logger.info("Worker loop finished processing current queue.")

if __name__ == "__main__":
    mock_tasks = [
        "Absorb https://github.com/psf/black and create a code formatter skill.",
        "Write a python script that utilizes our newly absorbed code formatting capabilities."
    ]

    worker = OmniAgentWorker()
    worker.run_worker_loop(mock_tasks)
