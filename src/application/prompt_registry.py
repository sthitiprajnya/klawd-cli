import datetime as dt
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PromptVersionRecord:
    version: str
    score: float
    promoted_at: dt.datetime | None = None
    rolled_back_at: dt.datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class PromptVersionRegistry:
    """Tracks prompt versions, evaluation metadata, promotions, and rollbacks."""

    def __init__(
        self,
        *,
        minimum_improvement_threshold: float = 0.05,
        notifier: callable | None = None,
        audit_logger: callable | None = None,
    ):
        self.minimum_improvement_threshold = minimum_improvement_threshold
        self.notifier = notifier or (lambda _event: None)
        self.audit_logger = audit_logger or (lambda _event: None)
        self._versions: dict[str, PromptVersionRecord] = {}
        self._active_version: str | None = None

    @property
    def active_version(self) -> str | None:
        return self._active_version

    def register_version(self, version: str, base_score: float = 0.0) -> PromptVersionRecord:
        record = PromptVersionRecord(version=version, score=base_score)
        self._versions[version] = record
        if self._active_version is None:
            self._active_version = version
        return record

    def get_record(self, version: str) -> PromptVersionRecord:
        return self._versions[version]

    def _build_rubric(self, recent_job_outcomes: list[dict[str, Any]], reviewer_artifacts: list[dict[str, Any]]) -> dict[str, float]:
        success_count = sum(1 for outcome in recent_job_outcomes if outcome.get("status") == "completed")
        completion_rate = success_count / max(1, len(recent_job_outcomes))

        pass_count = sum(1 for artifact in reviewer_artifacts if artifact.get("status") in {"pass", "pass_with_notes"})
        review_pass_rate = pass_count / max(1, len(reviewer_artifacts))

        avg_static_findings = sum(artifact.get("static_findings", 0) for artifact in reviewer_artifacts) / max(1, len(reviewer_artifacts))
        static_quality = max(0.0, 1.0 - (avg_static_findings / 10.0))

        return {
            "completion_rate": completion_rate,
            "review_pass_rate": review_pass_rate,
            "static_quality": static_quality,
        }

    def evaluate_candidate(
        self,
        *,
        candidate_version: str,
        recent_job_outcomes: list[dict[str, Any]],
        reviewer_artifacts: list[dict[str, Any]],
        held_out_score: float,
    ) -> tuple[float, dict[str, float]]:
        rubric = self._build_rubric(recent_job_outcomes, reviewer_artifacts)
        weighted_score = (
            (rubric["completion_rate"] * 0.35)
            + (rubric["review_pass_rate"] * 0.35)
            + (rubric["static_quality"] * 0.10)
            + (held_out_score * 0.20)
        )

        self._versions.setdefault(candidate_version, PromptVersionRecord(version=candidate_version, score=0.0))
        return weighted_score, rubric

    def try_promote(
        self,
        *,
        candidate_version: str,
        recent_job_outcomes: list[dict[str, Any]],
        reviewer_artifacts: list[dict[str, Any]],
        held_out_score: float,
    ) -> bool:
        candidate_score, rubric = self.evaluate_candidate(
            candidate_version=candidate_version,
            recent_job_outcomes=recent_job_outcomes,
            reviewer_artifacts=reviewer_artifacts,
            held_out_score=held_out_score,
        )
        current_score = self._versions[self._active_version].score if self._active_version else 0.0
        improvement = candidate_score - current_score

        if improvement < self.minimum_improvement_threshold:
            event = {
                "event": "prompt_promotion_rejected",
                "candidate_version": candidate_version,
                "candidate_score": candidate_score,
                "current_version": self._active_version,
                "current_score": current_score,
                "improvement": improvement,
                "threshold": self.minimum_improvement_threshold,
                "rubric": rubric,
                "held_out_score": held_out_score,
                "occurred_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            }
            self.audit_logger(event)
            self.notifier(event)
            return False

        record = self._versions[candidate_version]
        record.score = candidate_score
        record.promoted_at = dt.datetime.now(dt.timezone.utc)
        record.rolled_back_at = None
        record.metadata = {"rubric": rubric, "held_out_score": held_out_score}
        self._active_version = candidate_version

        event = {
            "event": "prompt_promoted",
            "version": candidate_version,
            "score": candidate_score,
            "improvement": improvement,
            "threshold": self.minimum_improvement_threshold,
            "rubric": rubric,
            "held_out_score": held_out_score,
            "occurred_at": record.promoted_at.isoformat(),
        }
        self.audit_logger(event)
        self.notifier(event)
        return True

    def rollback(self, *, to_version: str, reason: str) -> PromptVersionRecord:
        if to_version not in self._versions:
            raise ValueError(f"Unknown version: {to_version}")

        now = dt.datetime.now(dt.timezone.utc)
        if self._active_version and self._active_version in self._versions:
            self._versions[self._active_version].rolled_back_at = now

        self._active_version = to_version
        record = self._versions[to_version]
        event = {
            "event": "prompt_rolled_back",
            "to_version": to_version,
            "reason": reason,
            "score": record.score,
            "rolled_back_at": now.isoformat(),
        }
        self.audit_logger(event)
        self.notifier(event)
        return record
