import json
import time
import logging
import re
import subprocess
from typing import Any, Tuple

from src.domain.agents import PlannerAgent, EngineerAgent, ReviewerAgent, AbsorberAgent
from src.domain.agents.reviewer import ReviewResult, ReviewStatus
from src.domain.skills import skill_manager
from src.infrastructure.memory.agent_memory import agent_memory
from src.infrastructure.security.execution_adapter import PolicyRejectionError

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

    def _run_static_review_hooks(self, code: str) -> list[dict[str, Any]]:
        """Deterministic static review pipeline hook.

        Contract (parseable): list[dict] with keys:
        tool, status, severity, message, rule_id, line.
        """
        cmd = ["semgrep", "--config=p/security-audit", "--json", "--quiet", "-"]
        try:
            result = subprocess.run(cmd, input=code.encode("utf-8"), capture_output=True, timeout=60)
            payload = json.loads(result.stdout.decode("utf-8") or "{}")
            findings = payload.get("results", [])
            return [
                {
                    "tool": "semgrep",
                    "status": "hit",
                    "severity": f.get("extra", {}).get("severity", "INFO"),
                    "message": f.get("extra", {}).get("message", ""),
                    "rule_id": f.get("check_id", "unknown"),
                    "line": f.get("start", {}).get("line", 0),
                }
                for f in findings
            ]
        except Exception as e:
            return [{"tool": "semgrep", "status": "error", "severity": "ERROR", "message": str(e), "rule_id": "hook_exception", "line": 0}]

    def process_absorption(self, task: str) -> bool:
        logger.info("Starting Absorption Protocol")
        raw_code = self.absorber.absorb_repo(task)
        clean_code = self._extract_code(raw_code)

        skill_name = f"skill_{int(time.time())}"
        if skill_manager.load_skill(skill_name, clean_code):
            agent_memory.store_outcome("Absorption Protocol", clean_code, f"Absorbed {skill_name}")
            return True
        return False

    def process_task(self, task: str) -> Tuple[str, str, str]:
        if "github.com" in task.lower() or "absorb" in task.lower():
            success = self.process_absorption(task)
            return "Absorption Task", "Code Saved", "Success" if success else "Failed"

        logger.info(f"Starting standard workflow: {task}")

        past_lessons = agent_memory.retrieve_lessons(context=task)
        skills = skill_manager.list_skills()
        context = f"Prior Lessons:\n{past_lessons}\nAvailable Skills: {skills}"

        try:
            plan = self.planner.create_plan(f"Task: {task}\nContext: {context}")
            code = self.engineer.write_code(plan)
        except PolicyRejectionError as e:
            payload = e.payload
            structured_error = f"WORKFLOW_POLICY_REJECTION|source={payload['source']}|reason={payload['reason']}|remediation={payload['remediation']}"
            return "PolicyBlocked", "", structured_error

        final_review = ReviewResult(status=ReviewStatus.FAIL_WITH_FEEDBACK, feedback="Initial pending review")
        for _ in range(self.max_iterations):
            try:
                review = self.reviewer.review_code(code)
            except PolicyRejectionError as e:
                payload = e.payload
                structured_error = f"REVIEWER_POLICY_REJECTION|source={payload['source']}|reason={payload['reason']}|remediation={payload['remediation']}"
                return plan, code, structured_error
            review.static_checks = self._run_static_review_hooks(code)
            review.metadata.update(
                {
                    "prism_validation_status": "unknown",
                    "nemoclaw_validation_status": "unknown",
                }
            )

            if review.status in {ReviewStatus.PASS, ReviewStatus.PASS_WITH_NOTES}:
                final_review = review
                break

            code = self.engineer.iterate_code(code, review.feedback)
            final_review = review

        reflection = self.reviewer.reflect(code, final_review.feedback)
        failure_class = "LOGIC" if final_review.status == ReviewStatus.FAIL_WITH_FEEDBACK else "NONE"
        review_artifact = {
            "status": final_review.status.value,
            "feedback": final_review.feedback,
            "static_checks": final_review.static_checks,
            "metadata": final_review.metadata,
            "failure_class": failure_class,
            "reflection": reflection,
        }
        agent_memory.store_outcome(task, code, json.dumps(review_artifact))

        return plan, code, final_review.feedback


workflow = OmniWorkflow()
