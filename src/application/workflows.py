import json
import time
import logging
import re
import subprocess
from typing import Any

from src.application.prompt_registry import PromptVersionRegistry

from src.domain.agents import PlannerAgent, EngineerAgent, ReviewerAgent, AbsorberAgent
from src.domain.agents.reviewer import ReviewResult, ReviewStatus
from src.domain.skills import skill_manager
from src.infrastructure.memory.agent_memory import agent_memory

logger = logging.getLogger("Workflows")

def _emit_audit_event(event: dict[str, Any]) -> None:
    logger.info("audit_event=%s", json.dumps(event))


def _send_notification(event: dict[str, Any]) -> None:
    logger.info("notification_event=%s", json.dumps(event))


class OmniWorkflow:
    def __init__(self):
        self.planner = PlannerAgent()
        self.engineer = EngineerAgent()
        self.reviewer = ReviewerAgent()
        self.absorber = AbsorberAgent()
        self.max_iterations = 3
        self.prompt_registry = PromptVersionRegistry(
            minimum_improvement_threshold=0.05,
            notifier=_send_notification,
            audit_logger=_emit_audit_event,
        )
        self.prompt_registry.register_version("v1", base_score=0.50)

    def _extract_code(self, text: str) -> str:
        match = re.search(r"```python\n(.*?)\n```", text, re.DOTALL)
        return match.group(1) if match else text

    def _run_static_review_hooks(self, code: str) -> list[dict[str, Any]]:
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
        raw_code = self.absorber.absorb_repo(task)
        clean_code = self._extract_code(raw_code)

        skill_name = f"skill_{int(time.time())}"
        if skill_manager.load_skill(skill_name, clean_code):
            agent_memory.store_outcome("Absorption Protocol", clean_code, f"Absorbed {skill_name}")
            return True
        return False

    def process_task(self, task: str) -> dict[str, Any]:
        started_at = time.time()

        if "github.com" in task.lower() or "absorb" in task.lower():
            success = self.process_absorption(task)
            return {
                "plan": "Absorption Task",
                "code": "Code Saved",
                "review_feedback": "Success" if success else "Failed",
                "status": "completed" if success else "failed",
                "review_artifact": {},
                "skills_absorbed": ["dynamic" if success else ""],
                "model_used": "n/a",
                "tokens_used": 0,
                "threat_score": 0,
                "latency_ms": int((time.time() - started_at) * 1000),
            }

        past_lessons = agent_memory.retrieve_lessons(context=task)
        skills = skill_manager.list_skills()
        context = f"Prior Lessons:\n{past_lessons}\nAvailable Skills: {skills}"

        plan = self.planner.create_plan(f"Task: {task}\nContext: {context}")
        code = self.engineer.write_code(plan)

        final_review = ReviewResult(status=ReviewStatus.FAIL_WITH_FEEDBACK, feedback="Initial pending review")
        for _ in range(self.max_iterations):
            review = self.reviewer.review_code(code)
            review.static_checks = self._run_static_review_hooks(code)
            review.metadata.update({"prism_validation_status": "unknown", "nemoclaw_validation_status": "unknown"})
            final_review = review
            if review.status in {ReviewStatus.PASS, ReviewStatus.PASS_WITH_NOTES}:
                break
            code = self.engineer.iterate_code(code, review.feedback)

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

        wf_status = "failed" if final_review.status == ReviewStatus.FAIL_WITH_FEEDBACK else "completed"
        return {
            "plan": plan,
            "code": code,
            "review_feedback": final_review.feedback,
            "status": wf_status,
            "review_artifact": review_artifact,
            "skills_absorbed": skills,
            "model_used": "router_default",
            "tokens_used": len(code.split()) + len(plan.split()),
            "threat_score": 0,
            "latency_ms": int((time.time() - started_at) * 1000),
        }


workflow = OmniWorkflow()
