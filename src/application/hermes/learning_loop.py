import typing
import datetime as dt
import hashlib
from dataclasses import dataclass
from typing import Any

from src.application.prompt_registry import EvalInputContract, PromptVersionRegistry


@dataclass(frozen=True)
class LearningCandidate:
    candidate_id: str
    candidate_version: str
    prompt_adjustment: str
    policy_adjustment: str
    model_metadata: dict[str, Any]
    diff_patch_hash: str
    rollback_pointer: str | None
    created_at: str


class HermesLearningCoordinator:
    def __init__(self, *, registry: PromptVersionRegistry, audit_logger: typing.Callable | None = None):
        self.registry = registry
        self.audit_logger = audit_logger or (lambda _event: None)
        self._seen_outcome_ids: set[str] = set()
        self._provenance: dict[str, dict[str, Any]] = {}

    def build_candidate_from_outcomes(self, *, workflow_outcomes: list[dict[str, Any]], model_metadata: dict[str, Any], reviewer_verdict: str) -> LearningCandidate | None:
        deduped = [o for o in workflow_outcomes if o.get("id") and o["id"] not in self._seen_outcome_ids]
        if not deduped:
            return None
        for item in deduped:
            self._seen_outcome_ids.add(item["id"])

        sample = deduped[-1]
        candidate_version = f"cand-{sample['id']}"
        prompt_adjustment = f"Tighten prompt for root:{sample.get('root_signature', 'unknown')}"
        policy_adjustment = "Increase deterministic checks before completion"
        diff_hash = hashlib.sha256(f"{prompt_adjustment}|{policy_adjustment}".encode()).hexdigest()
        created_at = dt.datetime.now(dt.timezone.utc).isoformat()
        candidate = LearningCandidate(
            candidate_id=sample["id"],
            candidate_version=candidate_version,
            prompt_adjustment=prompt_adjustment,
            policy_adjustment=policy_adjustment,
            model_metadata=model_metadata,
            diff_patch_hash=diff_hash,
            rollback_pointer=self.registry.active_version,
            created_at=created_at,
        )
        self._provenance[candidate.candidate_id] = {
            "candidate_id": candidate.candidate_id,
            "candidate_version": candidate.candidate_version,
            "model_metadata": model_metadata,
            "diff_patch_hash": candidate.diff_patch_hash,
            "reviewer_verdict": reviewer_verdict,
            "rollback_pointer": candidate.rollback_pointer,
        }
        self.audit_logger({"event": "learning_candidate_created", "candidate_id": candidate.candidate_id, "candidate_version": candidate.candidate_version, "job_id": sample.get("job_id"), "occurred_at": created_at})
        return candidate

    def promote_candidate(self, *, candidate: LearningCandidate, eval_input: EvalInputContract, recent_job_outcomes: list[dict[str, Any]], reviewer_artifacts: list[dict[str, Any]], held_out_score: float, safety_metrics: dict[str, float], baseline_safety_metrics: dict[str, float], retry_budget_remaining: int) -> bool:
        promoted = self.registry.try_promote(candidate_version=candidate.candidate_version, recent_job_outcomes=recent_job_outcomes, reviewer_artifacts=reviewer_artifacts, held_out_score=held_out_score, eval_input=eval_input, safety_metrics=safety_metrics, baseline_safety_metrics=baseline_safety_metrics, retry_budget_remaining=retry_budget_remaining)
        self.audit_logger({"event": "learning_candidate_promoted" if promoted else "learning_candidate_rejected", "candidate_id": candidate.candidate_id, "candidate_version": candidate.candidate_version, "job_id": candidate.candidate_id, "occurred_at": dt.datetime.now(dt.timezone.utc).isoformat()})
        return promoted

    def rollback_candidate(self, *, candidate: LearningCandidate, reason: str) -> None:
        if candidate.rollback_pointer:
            self.registry.rollback(to_version=candidate.rollback_pointer, reason=reason)
        self.audit_logger({"event": "learning_candidate_rolled_back", "candidate_id": candidate.candidate_id, "candidate_version": candidate.candidate_version, "occurred_at": dt.datetime.now(dt.timezone.utc).isoformat()})

    def get_provenance(self, candidate_id: str) -> dict[str, Any]:
        return self._provenance[candidate_id]
