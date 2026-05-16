import re
import ipaddress
import time
from pathlib import Path
from collections import defaultdict, deque
from src.infrastructure.security.hooks import HookPoint, PRISMVerdict

# --- Mocks ---
def audit_log(hook, kwargs, verdict): pass
# -------------

INJECTION_PATTERNS = [r"ignore (all |previous )?instructions", r"jailbreak", r"system:\s*override"]

def h1_scan(prompt: str) -> PRISMVerdict:
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, prompt, re.IGNORECASE):
            return PRISMVerdict(allow=False, reason=f"injection_pattern:{pattern}")
    return PRISMVerdict(allow=True, reason="clean")

ROLE_TOOL_ALLOWLIST = {
    "coder": {"bash", "read_file", "write_file", "run_tests", "git_diff", "git_commit"},
    "absorber": {"git_clone", "wget", "npm_pack", "mempalace_bulk_import", "semgrep", "osv_query"}
}

def h2_scan(tool_name: str, agent_role: str, params: dict) -> PRISMVerdict:
    if tool_name not in ROLE_TOOL_ALLOWLIST.get(agent_role, set()):
        return PRISMVerdict(allow=False, reason=f"tool_not_allowed:{tool_name}@{agent_role}")
    if tool_name == "bash" and any(d in params.get("command", "") for d in ["rm -rf /", "chmod 777"]):
        return PRISMVerdict(allow=False, reason="dangerous_bash")
    return PRISMVerdict(allow=True, reason="tool_allowed")

def h3_scan(command: str) -> PRISMVerdict:
    parts = command.strip().split()
    if not parts: return PRISMVerdict(allow=True, reason="empty")
    if Path(parts[0]).name in {"sudo", "su", "mount"}:
        return PRISMVerdict(allow=False, reason="blocked_binary")
    return PRISMVerdict(allow=True, reason="clean")

def h4_scan(path: str) -> PRISMVerdict:
    if str(Path(path).resolve()).startswith("/etc/"):
        return PRISMVerdict(allow=False, reason="write_denied_path")
    return PRISMVerdict(allow=True, reason="path_allowed")

def h5_scan(url: str, agent_role: str) -> PRISMVerdict:
    if agent_role in ["coder", "qa", "memory"]:
        return PRISMVerdict(allow=False, reason="no_egress_role")
    return PRISMVerdict(allow=True, reason="host_allowed")

def h6_scan(raw_output: str) -> PRISMVerdict:
    if re.search(r"api[_-]?key\s*[:=]\s*['\"]?[A-Za-z0-9\-_]{20,}", raw_output, re.IGNORECASE):
        return PRISMVerdict(allow=False, reason="exfil_pattern")
    return PRISMVerdict(allow=True, reason="clean")

def h7_scan(content: str, wing: str, agent_role: str) -> PRISMVerdict:
    if agent_role == "coder" and wing == "orchestrator-diary":
        return PRISMVerdict(allow=False, reason="cross_wing_write")
    return PRISMVerdict(allow=True, reason="clean")

def h8_scan(skill_md: str, artifact: dict) -> PRISMVerdict:
    return PRISMVerdict(allow=True, reason="immunization_passed") # Mocks ImmunizationFilter pass

_active_agent_count = {}
def h9_scan(parent_agent_id: str, requested_count: int = 1) -> PRISMVerdict:
    current = _active_agent_count.get(parent_agent_id, 0)
    if current + requested_count > 8:
        return PRISMVerdict(allow=False, reason="subagent_limit_exceeded")
    _active_agent_count[parent_agent_id] = current + requested_count
    return PRISMVerdict(allow=True, reason="spawn_allowed")

_notify_log = defaultdict(lambda: deque(maxlen=100))
def h10_scan(severity: str, message: str) -> PRISMVerdict:
    now = time.time()
    window = _notify_log[severity]
    while window and now - window > 3600: window.popleft()
    if len(window) >= {"critical": 20, "warning": 10, "info": 5}.get(severity, 5):
        return PRISMVerdict(allow=False, reason="rate_limit_exceeded")
    window.append(now)
    return PRISMVerdict(allow=True, reason="notify_allowed")

HOOK_SCANNERS = {
    "h1_prompt_received": h1_scan, "h2_tool_requested": h2_scan,
    "h3_subprocess_spawn": h3_scan, "h4_file_write": h4_scan,
    "h5_network_egress": h5_scan, "h6_llm_output_raw": h6_scan,
    "h7_memory_write": h7_scan, "h8_skill_registration": h8_scan,
    "h9_agent_spawn": h9_scan, "h10_human_notify": h10_scan,
}

def prism_check(hook: str, **kwargs) -> PRISMVerdict:
    verdict = HOOK_SCANNERS[hook](**kwargs)
    if not verdict.allow: audit_log(hook, kwargs, verdict)
    return verdict