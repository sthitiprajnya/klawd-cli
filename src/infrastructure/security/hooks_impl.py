import logging
import re
import time
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any

from src.infrastructure.security.hooks import HookPoint, HookReason, HookSeverity, PRISMVerdict

logger = logging.getLogger("PRISMSecurity")


HOOK_METRICS: Counter[tuple[str, str, str]] = Counter()


def _record_metric(hook: str, allow: bool, reason: str) -> None:
    HOOK_METRICS[(hook, "allow" if allow else "deny", reason.split(":", 1)[0])] += 1


def _mk_verdict(
    *,
    hook: HookPoint,
    allow: bool,
    reason: HookReason | str,
    severity: HookSeverity = HookSeverity.INFO,
    evidence: list[str] | None = None,
    sanitized_payload: Any = None,
) -> PRISMVerdict:
    return PRISMVerdict(
        allow=allow,
        reason=reason.value if isinstance(reason, HookReason) else reason,
        hook=hook.value,
        severity=severity.value,
        evidence=evidence or [],
        sanitized_payload=sanitized_payload,
    )


def audit_log(hook: str, kwargs: dict[str, Any], verdict: PRISMVerdict) -> None:
    logger.warning(
        "PRISM BLOCKED - Hook: %s, Reason: %s, Severity: %s, Evidence: %s, Args: %s",
        hook,
        verdict.reason,
        verdict.severity,
        verdict.evidence,
        kwargs,
    )


INJECTION_PATTERNS = [r"ignore\s+(all\s+)?(previous\s+)?instructions", r"jailbreak", r"system:\s*override"]


def h1_scan(prompt: str) -> PRISMVerdict:
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, prompt, re.IGNORECASE):
            return _mk_verdict(
                hook=HookPoint.H1_PROMPT_RECEIVED,
                allow=False,
                reason=f"{HookReason.INJECTION_PATTERN.value}:{pattern}",
                severity=HookSeverity.CRITICAL,
                evidence=[pattern],
            )
    return _mk_verdict(hook=HookPoint.H1_PROMPT_RECEIVED, allow=True, reason=HookReason.CLEAN)


ROLE_TOOL_ALLOWLIST = {
    "coder": {"bash", "read_file", "write_file", "run_tests", "git_diff", "git_commit"},
    "absorber": {"git_clone", "wget", "npm_pack", "mempalace_bulk_import", "semgrep", "osv_query"},
}


def h2_scan(tool_name: str, agent_role: str, params: dict) -> PRISMVerdict:
    if tool_name not in ROLE_TOOL_ALLOWLIST.get(agent_role, set()):
        return _mk_verdict(
            hook=HookPoint.H2_TOOL_REQUESTED,
            allow=False,
            reason=f"{HookReason.TOOL_NOT_ALLOWED.value}:{tool_name}@{agent_role}",
            severity=HookSeverity.WARNING,
            evidence=[tool_name, agent_role],
        )
    if tool_name == "bash" and any(d in params.get("command", "") for d in ["rm -rf /", "chmod 777"]):
        return _mk_verdict(
            hook=HookPoint.H2_TOOL_REQUESTED,
            allow=False,
            reason=HookReason.DANGEROUS_BASH,
            severity=HookSeverity.CRITICAL,
            evidence=[params.get("command", "")],
        )
    return _mk_verdict(hook=HookPoint.H2_TOOL_REQUESTED, allow=True, reason=HookReason.TOOL_ALLOWED)


def h3_scan(command: str) -> PRISMVerdict:
    parts = command.strip().split()
    if not parts:
        return _mk_verdict(hook=HookPoint.H3_SUBPROCESS_SPAWN, allow=True, reason=HookReason.CLEAN)
    if Path(parts[0]).name in {"sudo", "su", "mount"}:
        return _mk_verdict(
            hook=HookPoint.H3_SUBPROCESS_SPAWN,
            allow=False,
            reason=HookReason.BLOCKED_BINARY,
            severity=HookSeverity.CRITICAL,
            evidence=[parts[0]],
        )
    return _mk_verdict(hook=HookPoint.H3_SUBPROCESS_SPAWN, allow=True, reason=HookReason.CLEAN)


def h4_scan(path: str) -> PRISMVerdict:
    if str(Path(path).resolve()).startswith("/etc/"):
        return _mk_verdict(
            hook=HookPoint.H4_FILE_WRITE,
            allow=False,
            reason=HookReason.WRITE_DENIED_PATH,
            severity=HookSeverity.CRITICAL,
            evidence=[path],
        )
    return _mk_verdict(hook=HookPoint.H4_FILE_WRITE, allow=True, reason=HookReason.PATH_ALLOWED)


def h5_scan(url: str, agent_role: str) -> PRISMVerdict:
    if agent_role in ["coder", "qa", "memory"]:
        return _mk_verdict(
            hook=HookPoint.H5_NETWORK_EGRESS,
            allow=False,
            reason=HookReason.NO_EGRESS_ROLE,
            severity=HookSeverity.WARNING,
            evidence=[url, agent_role],
        )
    return _mk_verdict(hook=HookPoint.H5_NETWORK_EGRESS, allow=True, reason=HookReason.HOST_ALLOWED)


def h6_scan(raw_output: str) -> PRISMVerdict:
    pattern = r"api[_-]?key\s*[:=]\s*['\"]?[A-Za-z0-9\-_]{20,}"
    if re.search(pattern, raw_output, re.IGNORECASE):
        return _mk_verdict(
            hook=HookPoint.H6_LLM_OUTPUT_RAW,
            allow=False,
            reason=HookReason.EXFIL_PATTERN,
            severity=HookSeverity.CRITICAL,
            evidence=["api_key_like_secret"],
        )
    return _mk_verdict(hook=HookPoint.H6_LLM_OUTPUT_RAW, allow=True, reason=HookReason.CLEAN)


def h7_scan(content: str, wing: str, agent_role: str) -> PRISMVerdict:
    if agent_role == "coder" and wing == "orchestrator-diary":
        return _mk_verdict(
            hook=HookPoint.H7_MEMORY_WRITE,
            allow=False,
            reason=HookReason.CROSS_WING_WRITE,
            severity=HookSeverity.WARNING,
            evidence=[wing, agent_role],
        )
    return _mk_verdict(hook=HookPoint.H7_MEMORY_WRITE, allow=True, reason=HookReason.CLEAN)


def h8_scan(skill_md: str, artifact: dict | None) -> PRISMVerdict:
    if not skill_md.strip():
        return _mk_verdict(hook=HookPoint.H8_SKILL_REGISTRATION, allow=False, reason=HookReason.EMPTY_SKILL_DEFINITION)
    if not artifact or not artifact.get("source"):
        return _mk_verdict(hook=HookPoint.H8_SKILL_REGISTRATION, allow=False, reason=HookReason.MISSING_ARTIFACT_SOURCE)
    return _mk_verdict(hook=HookPoint.H8_SKILL_REGISTRATION, allow=True, reason=HookReason.CLEAN)


_active_agent_count: dict[str, int] = {}


def h9_scan(parent_agent_id: str, requested_count: int = 1) -> PRISMVerdict:
    current = _active_agent_count.get(parent_agent_id, 0)
    if current + requested_count > 8:
        return _mk_verdict(hook=HookPoint.H9_AGENT_SPAWN, allow=False, reason=HookReason.SUBAGENT_LIMIT_EXCEEDED)
    _active_agent_count[parent_agent_id] = current + requested_count
    return _mk_verdict(hook=HookPoint.H9_AGENT_SPAWN, allow=True, reason=HookReason.SPAWN_ALLOWED)


_notify_log = defaultdict(lambda: deque(maxlen=100))


def h10_scan(severity: str, message: str) -> PRISMVerdict:
    now = time.time()
    window = _notify_log[severity]
    while window and (now - window[0]) > 3600:
        window.popleft()
    if len(window) >= {"critical": 20, "warning": 10, "info": 5}.get(severity, 5):
        return _mk_verdict(hook=HookPoint.H10_HUMAN_NOTIFY, allow=False, reason=HookReason.RATE_LIMIT_EXCEEDED)
    window.append(now)
    return _mk_verdict(hook=HookPoint.H10_HUMAN_NOTIFY, allow=True, reason=HookReason.NOTIFY_ALLOWED)


HOOK_SCANNERS = {
    HookPoint.H1_PROMPT_RECEIVED.value: h1_scan,
    HookPoint.H2_TOOL_REQUESTED.value: h2_scan,
    HookPoint.H3_SUBPROCESS_SPAWN.value: h3_scan,
    HookPoint.H4_FILE_WRITE.value: h4_scan,
    HookPoint.H5_NETWORK_EGRESS.value: h5_scan,
    HookPoint.H6_LLM_OUTPUT_RAW.value: h6_scan,
    HookPoint.H7_MEMORY_WRITE.value: h7_scan,
    HookPoint.H8_SKILL_REGISTRATION.value: h8_scan,
    HookPoint.H9_AGENT_SPAWN.value: h9_scan,
    HookPoint.H10_HUMAN_NOTIFY.value: h10_scan,
}


def prism_check(hook: str, **kwargs) -> PRISMVerdict:
    scanner = HOOK_SCANNERS.get(hook)
    if scanner is None:
        verdict = _mk_verdict(hook=HookPoint.H1_PROMPT_RECEIVED, allow=False, reason=f"unknown_hook:{hook}")
        _record_metric(hook, verdict.allow, verdict.reason)
        return verdict
    try:
        verdict = scanner(**kwargs)
    except Exception as exc:
        verdict = PRISMVerdict(
            allow=True,
            reason=HookReason.HOOK_EXCEPTION.value,
            hook=hook,
            severity=HookSeverity.WARNING.value,
            evidence=[str(exc)],
        )
    _record_metric(hook, verdict.allow, verdict.reason)
    if not verdict.allow:
        audit_log(hook, kwargs, verdict)
    return verdict
