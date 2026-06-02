from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import shlex
import subprocess

from src.infrastructure.security.hooks_impl import prism_check


_UNSAFE_BG_PATTERN = re.compile(r"(?:^|\s)(?:&|nohup\b|disown\b|setsid\b)", re.IGNORECASE)


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


    def _tokenize_command(self, command: str) -> list[str]:
        # CVE-2025-35028 mitigation: canonicalize free-form command strings using
        # POSIX-aware tokenization before spawn so meta characters are not shell-interpreted.
        return shlex.split(command)

    def _validate_background_patterns(self, command: str) -> None:
        # CVE-2025-35028 mitigation: reject shell-style background/process-detach syntax
        # to prevent daemonization or hidden child process persistence.
        if _UNSAFE_BG_PATTERN.search(command):
            raise PolicyRejectionError(
                source="nemoclaw",
                reason="unsafe_background_process_pattern",
                remediation="Remove background-process syntax (e.g. &, nohup, disown, setsid) and retry.",
            )

    def spawn_command(self, command: str) -> subprocess.Popen:
        self._validate_background_patterns(command)
        argv = self._tokenize_command(command)
        # CVE-2025-35028 mitigation: never execute through a shell.
        return subprocess.Popen(argv, shell=False)

execution_adapter = NemoClawExecutionAdapter()
