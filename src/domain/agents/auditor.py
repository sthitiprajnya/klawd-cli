from __future__ import annotations

from src.settings import EXTERNAL_SKILL_SOURCES

from .base import BaseAgent

AUDITOR_PROMPT = """You are Delta, a benign code auditor.
Analyze supplied code and metadata for safety, configuration hygiene, and compliance gaps.
Return concise findings suitable for reviewer context."""


class AuditorAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Delta", role="Auditor", system_prompt=AUDITOR_PROMPT)

    def audit_codebase(self, code_artifact: str, audit_context: dict | None = None, openhuman_context: dict | None = None) -> str:
        prompt = f"Code Artifact:\n{code_artifact}"
        if audit_context:
            prompt += f"\n\nAudit Context: {audit_context}"
        if openhuman_context:
            prompt += f"\n\nOpenHuman Context: {openhuman_context}"
        return self.process(prompt, task_type="complex").strip()
class HexStrikeClient:
    """MCP-style client for benign recon insights from HexStrike knowledge sources."""

    def __init__(self) -> None:
        self.source = next((s for s in EXTERNAL_SKILL_SOURCES if s.name == "hexstrike_ai"), None)

    def benign_recon_context(self, target: str) -> dict:
        if not self.source:
            return {"provider": "hexstrike_ai", "enabled": False, "summary": "HexStrike source not configured."}
        return {
            "provider": self.source.name,
            "enabled": self.source.enabled,
            "repo_url": self.source.repo_url,
            "pinned_ref": self.source.pinned_ref,
            "target": target,
            "summary": "Use for authorized passive recon, surface mapping, and defensive posture discovery.",
        }


class CyberStrikeClient:
    """MCP-style client for compliance benchmark and secure-baseline references."""

    def __init__(self) -> None:
        self.source = next((s for s in EXTERNAL_SKILL_SOURCES if s.name == "cyberstrike"), None)

    def compliance_benchmark_context(self, framework: str = "CIS") -> dict:
        if not self.source:
            return {"provider": "cyberstrike", "enabled": False, "summary": "CyberStrike source not configured."}
        return {
            "provider": self.source.name,
            "enabled": self.source.enabled,
            "repo_url": self.source.repo_url,
            "pinned_ref": self.source.pinned_ref,
            "framework": framework,
            "summary": "Use for secure baseline checks, controls mapping, and remediation benchmark references.",
        }


