from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CapabilityRoute:
    stage: str
    enabled: dict[str, bool]
    fallback_reason: str | None = None


_DEFAULT_STAGE_CAPABILITIES: dict[str, dict[str, bool]] = {
    "plan": {"dynamic_context": True, "safety_scoring": True, "learning_signals": True},
    "execute": {"dynamic_context": True, "safety_scoring": True, "provider_metadata": True},
    "review": {"dynamic_context": True, "safety_scoring": True, "reflect": True},
    "failure": {"dynamic_context": False, "safety_scoring": True, "learning_signals": True},
}


def resolve_capabilities(stage: str, *, openhuman_available: bool, overrides: dict[str, Any] | None = None) -> CapabilityRoute:
    base = dict(_DEFAULT_STAGE_CAPABILITIES.get(stage, {}))
    if overrides:
        for key, value in overrides.items():
            if key in base and isinstance(value, bool):
                base[key] = value

    if not openhuman_available:
        return CapabilityRoute(stage=stage, enabled={k: False for k in base}, fallback_reason="openhuman_unavailable")

    return CapabilityRoute(stage=stage, enabled=base)
