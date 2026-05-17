import time
import logging
import re
from typing import Tuple
from src.domain.agents import PlannerAgent, EngineerAgent, ReviewerAgent, AbsorberAgent
from src.domain.skills import skill_manager
from src.infrastructure.database import SessionLocal, MemoryEntry

logger = logging.getLogger("Workflows")

class OmniWorkflow:
    def __init__(self):
        self.planner = PlannerAgent()
        self.engineer = EngineerAgent()
        self.reviewer = ReviewerAgent()
        self.absorber = AbsorberAgent()
        self.max_iterations = 3

    def _extract_code(self, text: str) -> str:
        match = re.search(r"```python\n(.*?)\n```", text, re.DOTALL)
        return match.group(1) if match else text

    def store_memory(self, task: str, code: str, feedback: str):
        db = SessionLocal()
        try:
            entry = MemoryEntry(task=task, result=code, feedback=feedback)
            db.add(entry)
            db.commit()
        finally:
            db.close()

    def get_memory_context(self) -> str:
        db = SessionLocal()
        try:
            entries = db.query(MemoryEntry).order_by(MemoryEntry.id.desc()).limit(3).all()
            return "\n".join([f"Task: {e.task}\nResult: {e.result}" for e in entries])
        finally:
            db.close()

    def process_absorption(self, task: str) -> bool:
        logger.info("Starting Absorption Protocol")
        raw_code = self.absorber.absorb_repo(task)
        clean_code = self._extract_code(raw_code)

        skill_name = f"skill_{int(time.time())}"
        if skill_manager.load_skill(skill_name, clean_code):
            self.store_memory("Absorption Protocol", clean_code, f"Absorbed {skill_name}")
            return True
        return False

    def process_task(self, task: str) -> Tuple[str, str, str]:
        if "github.com" in task.lower() or "absorb" in task.lower():
            success = self.process_absorption(task)
            return "Absorption Task", "Code Saved", "Success" if success else "Failed"

        logger.info(f"Starting standard workflow: {task}")

        past_lessons = self.get_memory_context()
        skills = skill_manager.list_skills()
        context = f"Prior Lessons:\n{past_lessons}\nAvailable Skills: {skills}"

        plan = self.planner.create_plan(f"Task: {task}\nContext: {context}")
        code = self.engineer.write_code(plan)

        final_review = "APPROVED"
        for i in range(self.max_iterations):
            review = self.reviewer.review_code(code)
            if "APPROVED" in review and i > 0:
                final_review = review
                break
            elif "APPROVED" in review:
                review = "[MOCK] Ensure edge case handling."

            code = self.engineer.iterate_code(code, review)
            final_review = review

        reflection = self.reviewer.reflect(code, final_review)
        self.store_memory(task, code, f"Feedback: {final_review}\nMeta: {reflection}")

        return plan, code, final_review

workflow = OmniWorkflow()
