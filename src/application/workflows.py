import json
import logging
import re
import subprocess
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from src.application.orchestration.failure_classifier import classify_failure
from src.domain.agents import AbsorberAgent, EngineerAgent, PlannerAgent, ReviewerAgent
from src.domain.agents.reviewer import ReviewResult, ReviewStatus
from src.domain.skills import skill_manager
from src.infrastructure.memory.agent_memory import agent_memory
from src.infrastructure.openhuman.capability_router import resolve_capabilities
from src.infrastructure.security.hooks import HookPoint
from src.infrastructure.security.hooks_impl import prism_check
from src.settings import settings

logger = logging.getLogger("Workflows")


@dataclass
class OpenHumanContext:
    request_id: str
    capability_flags: dict[str, bool]
    safety_verdicts: dict[str, Any] = field(default_factory=dict)
    latency_budget_ms: int = 2000
    provider_metadata: dict[str, Any] = field(default_factory=dict)
    learning_signals: dict[str, Any] = field(default_factory=dict)
    openhuman_status: str = "available"
    fallback_reason: str | None = None


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

    def _run_static_review_hooks(self, code: str) -> list[dict[str, Any]]:
        try:
            result = subprocess.run(["semgrep", "--config=p/security-audit", "--json", "--quiet", "-"], input=code.encode(), capture_output=True, timeout=60)
            findings = json.loads(result.stdout.decode() or "{}").get("results", [])
            return [{"tool": "semgrep", "status": "hit", "severity": f.get("extra", {}).get("severity", "INFO")} for f in findings]
        except Exception as exc:
            return [{"tool": "semgrep", "status": "error", "message": str(exc)}]

    def _build_openhuman_context(self, task: str, stage: str) -> OpenHumanContext:
        obs = getattr(self.planner, "last_openhuman_observability", {})
        available = bool(obs.get("openhuman_available", True))
        route = resolve_capabilities(stage, openhuman_available=available)
        degraded = not available or obs.get("openhuman_error") == "timeout"
        return OpenHumanContext(
            request_id=f"req_{int(time.time() * 1000)}",
            capability_flags=route.enabled,
            safety_verdicts={"prism": "unknown", "nemoclaw": "unknown", "openhuman_score": None},
            latency_budget_ms=2000,
            provider_metadata={"provider": "openhuman", "stage": stage, "task_hash": hash(task)},
            learning_signals={"attempt": 1},
            openhuman_status="degraded" if degraded else "available",
            fallback_reason=route.fallback_reason if degraded else None,
        )

    def process_task(self, task: str):
        inbound_verdict = prism_check(HookPoint.H1_PROMPT_RECEIVED.value, prompt=task)
        if not inbound_verdict.allow:
            return "Blocked", "", inbound_verdict.reason

        lessons = agent_memory.retrieve_lessons(context=task, top_k=settings.mempalace_semantic_top_k)
        context = f"Prior Lessons:\n{lessons[:settings.mempalace_semantic_max_chars]}"

        oh_ctx = self._build_openhuman_context(task, "plan")
        plan = self.planner.create_plan(f"Task: {task}\nContext: {context}", openhuman_context=asdict(oh_ctx))

        oh_ctx = self._build_openhuman_context(task, "execute")
        code = self.engineer.write_code(plan, openhuman_context=asdict(oh_ctx))

        final_review = ReviewResult(status=ReviewStatus.FAIL_WITH_FEEDBACK, feedback="")
        for i in range(self.max_iterations):
            oh_ctx = self._build_openhuman_context(task, "review")
            review = self.reviewer.review_code(code, openhuman_context=asdict(oh_ctx))
            review.static_checks = self._run_static_review_hooks(code)
            review.metadata.update({
                "telemetry": {
                    "prism": "unknown",
                    "nemoclaw": "unknown",
                    "openhuman": getattr(self.reviewer, "last_openhuman_observability", {}),
                },
                "openhuman_status": oh_ctx.openhuman_status,
            })
            final_review = review
            if review.status in {ReviewStatus.PASS, ReviewStatus.PASS_WITH_NOTES}:
                break
            if i < self.max_iterations - 1:
                code = self.engineer.iterate_code(code, review.feedback, openhuman_context=asdict(oh_ctx))

        reflection = self.reviewer.reflect(code, final_review.feedback, openhuman_context=asdict(oh_ctx))
        failure_class = classify_failure(final_review.feedback) if final_review.status == ReviewStatus.FAIL_WITH_FEEDBACK else "NONE"
        review_artifact = {
            "status": final_review.status.value,
            "feedback": final_review.feedback,
            "static_checks": final_review.static_checks,
            "metadata": final_review.metadata,
            "failure_class": failure_class,
            "reflection": reflection,
            "openhuman_context": asdict(oh_ctx),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        agent_memory.store_outcome(
            task,
            code,
            json.dumps(review_artifact),
            status=final_review.status.value,
            failure_class=failure_class,
            metadata={
                "capabilities_used": oh_ctx.capability_flags,
                "risk_flags": review_artifact["metadata"]["telemetry"],
                "confidence": "high" if final_review.status != ReviewStatus.FAIL_WITH_FEEDBACK else "low",
                "fallback_reason": oh_ctx.fallback_reason,
                "openhuman_status": oh_ctx.openhuman_status,
            },
        )
        return plan, code, final_review.feedback


workflow = OmniWorkflow()
