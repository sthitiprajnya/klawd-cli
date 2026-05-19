from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.infrastructure.security.hooks_impl import prism_check


class PolicyRejectionError(RuntimeError):
    def __init__(self, *, source: str, reason: str, remediation: str):
        self.payload = {
            "error_type": "policy_rejection",
            "source": source,
            "reason": reason,
            "remediation": remediation,
        }
        super().__init__(str(self.payload))


@dataclass
class NemoClawHealth:
    status: str
    reason: str


class NemoClawExecutionAdapter:
    def __init__(self, policy_file: str = "nemoclaw-policy.yaml"):
        self.policy_file = Path(policy_file)

    def startup_validate(self) -> None:
        if not self.policy_file.exists():
            raise PolicyRejectionError(
                source="nemoclaw",
                reason="policy_file_missing",
                remediation=f"Add required policy file at {self.policy_file}",
            )

    def health(self) -> NemoClawHealth:
        if not self.policy_file.exists():
            return NemoClawHealth(status="down", reason="policy_file_missing")
        return NemoClawHealth(status="up", reason="ok")

    def execute(self, *, prompt: str, task_type: str, command: str | None = None) -> None:
        h = self.health()
        is_doc_task = task_type == "documentation"
        is_exec_task = task_type in {"coding", "complex", "fast", "reflection"}

        if h.status != "up" and is_exec_task and not is_doc_task:
            raise PolicyRejectionError(
                source="nemoclaw",
                reason="sandbox_down_execution_blocked",
                remediation="Restore NemoClaw health before running code-execution tasks, or submit a documentation-only task.",
            )

        if command and is_exec_task:
            verdict = prism_check("h3_subprocess_spawn", command=command)
            if not verdict.allow:
                raise PolicyRejectionError(
                    source="nemoclaw",
                    reason=f"command_blocked:{verdict.reason}",
                    remediation="Use an allowed non-privileged command and retry.",
                )


execution_adapter = NemoClawExecutionAdapter()
