import json
import time
import logging
import re
import subprocess
from datetime import datetime, timezone
from typing import Any, Tuple
from dataclasses import dataclass, asdict, field
from typing import Any, Callable, Tuple

from src.domain.agents import PlannerAgent, EngineerAgent, ReviewerAgent, AbsorberAgent
from src.domain.agents.reviewer import ReviewResult, ReviewStatus
from src.domain.skills import skill_manager
from src.infrastructure.memory.agent_memory import agent_memory
from src.infrastructure.security.execution_adapter import PolicyRejectionError
from src.infrastructure.security.hooks import HookPoint
from src.infrastructure.security.hooks_impl import prism_check

logger = logging.getLogger("Workflows")

def _emit_audit_event(event: dict[str, Any]) -> None:
    logger.info("audit_event=%s", json.dumps(event))


def _send_notification(event: dict[str, Any]) -> None:
    logger.info("notification_event=%s", json.dumps(event))


@dataclass
class WorkflowSnapshot:
    state: str = "plan"
    task: str = ""
    plan: str = ""
    code: str = ""
    review_feedback: str = ""
    review_status: str = ReviewStatus.FAIL_WITH_FEEDBACK.value
    retries: int = 0
    max_retries: int = 0
    completed: bool = False
    static_checks: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class OmniWorkflow:
    def __init__(self):
        self.planner = PlannerAgent()
        self.engineer = EngineerAgent()
        self.reviewer = ReviewerAgent()
        self.absorber = AbsorberAgent()
        self.max_iterations = 3
        self._snapshots: dict[str, WorkflowSnapshot] = {}
        self._event_sinks: list[Callable[[dict[str, Any]], None]] = [self._telemetry_sink]

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
        outbound_verdict = prism_check(HookPoint.H6_LLM_OUTPUT_RAW.value, raw_output=clean_code)
        if not outbound_verdict.allow:
            return False

        if skill_manager.load_skill(skill_name, clean_code):
            agent_memory.store_outcome("Absorption Protocol", clean_code, f"Absorbed {skill_name}")
            return True
        return False

    def register_event_sink(self, sink: Callable[[dict[str, Any]], None]) -> None:
        self._event_sinks.append(sink)

    def _telemetry_sink(self, event: dict[str, Any]) -> None:
        logger.info("workflow_transition", extra={"workflow_event": event})

    def _emit_transition(self, task: str, from_state: str, to_state: str, snapshot: WorkflowSnapshot) -> None:
        event = {
            "type": "workflow_transition",
            "task": task,
            "from_state": from_state,
            "to_state": to_state,
            "retries": snapshot.retries,
            "max_retries": snapshot.max_retries,
            "review_status": snapshot.review_status,
        }
        for sink in self._event_sinks:
            try:
                sink(event)
            except Exception as exc:
                logger.warning("event sink failed: %s", exc)

    def _persist_snapshot(self, task: str, snapshot: WorkflowSnapshot) -> None:
        self._snapshots[task] = snapshot

    def _load_snapshot(self, task: str) -> WorkflowSnapshot | None:
        return self._snapshots.get(task)

    def process_task(self, task: str) -> Tuple[str, str, str]:
        inbound_verdict = prism_check(HookPoint.H1_PROMPT_RECEIVED.value, prompt=task)
        if not inbound_verdict.allow:
            return "Blocked", "", inbound_verdict.reason
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
        snapshot = self._load_snapshot(task) or WorkflowSnapshot(task=task, max_retries=self.max_iterations)
        final_review = ReviewResult(status=ReviewStatus.FAIL_WITH_FEEDBACK, feedback="Initial pending review")

        while not snapshot.completed:
            state = snapshot.state
            if state == "plan":
                snapshot.plan = self.planner.create_plan(f"Task: {task}\nContext: {context}")
                self._emit_transition(task, "plan", "execute", snapshot)
                snapshot.state = "execute"
                self._persist_snapshot(task, snapshot)
            elif state == "execute":
                if snapshot.code and snapshot.retries > 0:
                    self._emit_transition(task, "execute", "review", snapshot)
                else:
                    snapshot.code = self.engineer.write_code(snapshot.plan)
                    self._emit_transition(task, "execute", "review", snapshot)
                snapshot.state = "review"
                self._persist_snapshot(task, snapshot)
            elif state == "review":
                review = self.reviewer.review_code(snapshot.code)
                review.static_checks = self._run_static_review_hooks(snapshot.code)
                review.metadata.update({"prism_validation_status": "unknown", "nemoclaw_validation_status": "unknown"})
                snapshot.review_feedback = review.feedback
                snapshot.review_status = review.status.value
                snapshot.static_checks = review.static_checks
                snapshot.metadata = review.metadata
                final_review = review
                break

            code = self.engineer.iterate_code(code, review.feedback)
            final_review = review

        output_verdict = prism_check(HookPoint.H6_LLM_OUTPUT_RAW.value, raw_output=code)
        if not output_verdict.allow:
            return plan, "", output_verdict.reason

        reflection = self.reviewer.reflect(code, final_review.feedback)
                next_state = "finalize" if review.status in {ReviewStatus.PASS, ReviewStatus.PASS_WITH_NOTES} else "iterate"
                self._emit_transition(task, "review", next_state, snapshot)
                snapshot.state = next_state
                self._persist_snapshot(task, snapshot)
            elif state == "iterate":
                if snapshot.retries >= snapshot.max_retries:
                    self._emit_transition(task, "iterate", "finalize", snapshot)
                    snapshot.state = "finalize"
                else:
                    snapshot.code = self.engineer.iterate_code(snapshot.code, snapshot.review_feedback)
                    snapshot.retries += 1
                    self._emit_transition(task, "iterate", "execute", snapshot)
                    snapshot.state = "execute"
                self._persist_snapshot(task, snapshot)
            elif state == "finalize":
                snapshot.completed = True
                self._persist_snapshot(task, snapshot)
            else:
                raise ValueError(f"Unknown workflow state: {state}")

        reflection = self.reviewer.reflect(snapshot.code, final_review.feedback)
        failure_class = "LOGIC" if final_review.status == ReviewStatus.FAIL_WITH_FEEDBACK else "NONE"
        now = datetime.now(timezone.utc).isoformat()
        review_artifact = {
            "status": final_review.status.value,
            "feedback": final_review.feedback,
            "static_checks": snapshot.static_checks,
            "metadata": snapshot.metadata,
            "failure_class": failure_class,
            "reflection": reflection,
            "snapshot": asdict(snapshot),
        }
        agent_memory.store_outcome(
            task,
            code,
            json.dumps(review_artifact),
            job_id=f"job_{int(time.time() * 1000)}",
            agent="omni_workflow",
            status=final_review.status.value,
            failure_class=failure_class,
        )
        agent_memory.store_outcome(task, snapshot.code, json.dumps(review_artifact))

        return snapshot.plan, snapshot.code, final_review.feedback


workflow = OmniWorkflow()
