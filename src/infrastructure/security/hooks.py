from enum import Enum
from dataclasses import dataclass
from typing import Any

class HookPoint(Enum):
    H1_PROMPT_RECEIVED     = "h1_prompt_received"
    H2_TOOL_REQUESTED      = "h2_tool_requested"
    H3_SUBPROCESS_SPAWN    = "h3_subprocess_spawn"
    H4_FILE_WRITE          = "h4_file_write"
    H5_NETWORK_EGRESS      = "h5_network_egress"
    H6_LLM_OUTPUT_RAW      = "h6_llm_output_raw"
    H7_MEMORY_WRITE        = "h7_memory_write"
    H8_SKILL_REGISTRATION  = "h8_skill_registration"
    H9_AGENT_SPAWN         = "h9_agent_spawn"
    H10_HUMAN_NOTIFY       = "h10_human_notify"

@dataclass
class PRISMVerdict:
    allow: bool
    reason: str
    sanitized_payload: Any = None