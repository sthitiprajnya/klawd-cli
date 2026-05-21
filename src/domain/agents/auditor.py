from __future__ import annotations
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

from src.settings import EXTERNAL_SKILL_SOURCES

from .base import BaseAgent

AUDITOR_PROMPT = """You are Delta, a benign code auditor.
Analyze supplied code and metadata for safety, configuration hygiene, and compliance gaps.
Return concise findings suitable for reviewer context."""


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


class AuditorAgent(BaseAgent):
    def __init__(self, *, hexstrike_client: HexStrikeClient | None = None, cyberstrike_client: CyberStrikeClient | None = None):
        super().__init__(name="Dana", role="Auditor", system_prompt=AUDITOR_PROMPT)
        self.hexstrike_client = hexstrike_client or HexStrikeClient()
        self.cyberstrike_client = cyberstrike_client or CyberStrikeClient()

    def audit_codebase(self, code_artifact: str, audit_context: dict | None = None, openhuman_context: dict | None = None) -> str:
        prompt = f"Code Artifact:\n{code_artifact}"
        if audit_context:
            prompt += f"\n\nAudit Context: {audit_context}"
        if openhuman_context:
            prompt += f"\n\nOpenHuman Context: {openhuman_context}"
        return self.process(prompt, task_type="complex").strip()

    def get_benign_recon_context(self, target: str) -> dict:
        return self.hexstrike_client.benign_recon_context(target)

    def get_compliance_benchmark_context(self, framework: str = "CIS") -> dict:
        return self.cyberstrike_client.compliance_benchmark_context(framework)

    def run_audit(self, target: str, scope: str, framework: str = "CIS", openhuman_context: dict | None = None) -> str:
        recon_context = self.get_benign_recon_context(target)
        compliance_context = self.get_compliance_benchmark_context(framework)
        prompt = (
            f"Target: {target}\n"
            f"Scope: {scope}\n"
            f"Recon Context: {recon_context}\n"
            f"Compliance Context: {compliance_context}\n\n"
            "Produce a defensive audit report with findings, risk severity, evidence expectations, and remediation steps."
        )
        if openhuman_context:
            prompt += f"\n\nOpenHuman Context: {openhuman_context}"
        return self.process(prompt, task_type="complex")

    def iterate_audit(self, prior_report: str, feedback: str, target: str, framework: str = "CIS", openhuman_context: dict | None = None) -> str:
        recon_context = self.get_benign_recon_context(target)
        compliance_context = self.get_compliance_benchmark_context(framework)
        prompt = (
            f"Prior Audit Report:\n{prior_report}\n\n"
            f"Feedback:\n{feedback}\n\n"
            f"Updated Recon Context: {recon_context}\n"
            f"Updated Compliance Context: {compliance_context}\n\n"
            "Refine the report with clearer prioritization, residual risk notes, and remediation validation criteria."
        )
        if openhuman_context:
            prompt += f"\n\nOpenHuman Context: {openhuman_context}"
        return self.process(prompt, task_type="complex")
