from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class HookPoint(Enum):
    H1_PROMPT_RECEIVED = "h1_prompt_received"
    H2_TOOL_REQUESTED = "h2_tool_requested"
    H3_SUBPROCESS_SPAWN = "h3_subprocess_spawn"
    H4_FILE_WRITE = "h4_file_write"
    H5_NETWORK_EGRESS = "h5_network_egress"
    H6_LLM_OUTPUT_RAW = "h6_llm_output_raw"
    H7_MEMORY_WRITE = "h7_memory_write"
    H8_SKILL_REGISTRATION = "h8_skill_registration"
    H9_AGENT_SPAWN = "h9_agent_spawn"
    H10_HUMAN_NOTIFY = "h10_human_notify"


class HookSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class HookReason(str, Enum):
    CLEAN = "clean"
    HOOK_EXCEPTION = "hook_exception"
    INJECTION_PATTERN = "injection_pattern"
    EXFIL_PATTERN = "exfil_pattern"
    TOOL_NOT_ALLOWED = "tool_not_allowed"
    DANGEROUS_BASH = "dangerous_bash"
    BLOCKED_BINARY = "blocked_binary"
    WRITE_DENIED_PATH = "write_denied_path"
    NO_EGRESS_ROLE = "no_egress_role"
    CROSS_WING_WRITE = "cross_wing_write"
    EMPTY_SKILL_DEFINITION = "empty_skill_definition"
    MISSING_ARTIFACT_SOURCE = "missing_artifact_source"
    INVALID_ARTIFACT_PROVENANCE = "invalid_artifact_provenance"
    SKILL_POLICY_VIOLATION = "skill_policy_violation"
    SECURITY_CONTEXT_REQUIRED = "security_context_required"
    SUBAGENT_LIMIT_EXCEEDED = "subagent_limit_exceeded"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    TOOL_ALLOWED = "tool_allowed"
    PATH_ALLOWED = "path_allowed"
    HOST_ALLOWED = "host_allowed"
    SPAWN_ALLOWED = "spawn_allowed"
    NOTIFY_ALLOWED = "notify_allowed"


@dataclass(frozen=True)
class HookInput:
    hook: HookPoint
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PRISMVerdict:
    allow: bool
    reason: str
    hook: str
    severity: str = HookSeverity.INFO.value
    evidence: list[str] = field(default_factory=list)
    sanitized_payload: Any = None
