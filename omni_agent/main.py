import time
import logging
import os
import re
from typing import List, Tuple, Optional

from omni_agent.agents import PlannerAgent, EngineerAgent, ReviewerAgent, AbsorberAgent
from omni_agent.utils.memory import agent_memory
from omni_agent.utils.skill_manager import skill_manager

logger = logging.getLogger("WorkerLoop")

class OmniAgentWorker:
    def __init__(self):
        self.planner = PlannerAgent()
        self.engineer = EngineerAgent()
        self.reviewer = ReviewerAgent()
        self.absorber = AbsorberAgent()
        self.max_iterations = 3

    def _extract_code_block(self, text: str) -> str:
        match = re.search(r"```python\n(.*?)\n```", text, re.DOTALL)
        if match:
            return match.group(1)
        return text

    def process_absorption(self, task: str) -> bool:
        """Special workflow for the Majin Buu absorption pattern."""
        logger.info("--- Starting Absorption Protocol ---")

        raw_skill_code = self.absorber.absorb_repo(task)
        clean_code = self._extract_code_block(raw_skill_code)

        skill_name = "absorbed_feature_" + str(int(time.time()))
        filepath = os.path.join("omni_agent", "skills", f"{skill_name}.py")

        with open(filepath, "w") as f:
            f.write(clean_code)

        logger.info(f"Feature absorbed and written to {filepath}")

        # Load safely using AST
        success = skill_manager.load_skill(skill_name)
        if not success:
             logger.warning("Absorption failed validation during AST parsing.")
             return False

        memory_entry = f"Successfully absorbed capability from {task}. Registered as {skill_name}."
        agent_memory.store_outcome("Absorption Protocol", clean_code, memory_entry)
        logger.info(f"Agent self-evolution complete. Now possesses {skill_name}.\n")
        return True

    def process_task(self, task: str) -> Tuple[str, str, str]:
        """Processes a single task through the entire agency lifecycle with deep self-evolution."""
        logger.info(f"--- Starting new task: {task} ---")

        active_skills = skill_manager.list_skills()
        skill_context = f"\nCurrently Absorbed Skills available: {active_skills}" if active_skills else ""

        past_lessons = agent_memory.retrieve_lessons(task)
        if past_lessons != "No past lessons found.":
            logger.info("Applying prior lessons to this task.")

        plan_prompt = f"Task: {task}\nPrior Context: {past_lessons}{skill_context}\nCreate a structured implementation pipeline."
        plan = self.planner.create_plan(plan_prompt)
        logger.info(f"Pipeline Plan generated.")

        code = self.engineer.write_code(plan)
        logger.info(f"Initial Code generated.")

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

        logger.info("Extracting meta-lessons from execution...")
        reflection = self.reviewer.reflect(code, final_review)

        agent_memory.store_outcome(task, code, f"Specific Feedback: {final_review}\nMeta-Lesson: {reflection}")
        logger.info("Task completed, evolved, reflected upon, and memorized.\n")

        return plan, code, final_review
