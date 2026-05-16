import subprocess, httpx
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any

@dataclass
class ThreatResult:
    category: str
    blocked: bool
    evidence: str = ""

@dataclass
class ImmunizationReport:
    artifact: dict
    findings: list[ThreatResult] = field(default_factory=list)

    def add(self, result: ThreatResult):
        self.findings.append(result)

def parse_semgrep_output(stdout: bytes) -> list[dict]:
    import json
    try:
        return json.loads(stdout).get("results", [])
    except Exception:
        return []

class ImmunizationFilter:
    OSV_API = "https://api.osv.dev/v1/query"

    def run(self, absorption_artifact: dict) -> ImmunizationReport:
        report = ImmunizationReport(artifact=absorption_artifact)
        report.add(self._check_prompt_injection(absorption_artifact.get("readme", "")))
        report.add(self._check_capability_escalation(absorption_artifact.get("skill_md", "")))
        report.add(self._check_malicious_code(absorption_artifact.get("source_files", [])))
        report.add(self._check_supply_chain(absorption_artifact.get("dependencies", [])))
        report.add(self._check_network_scope(absorption_artifact.get("skill_md", "")))
        return report

    def _check_prompt_injection(self, readme: str) -> ThreatResult:
        # MOCKED implementation
        return ThreatResult(category="PROMPT_INJECTION", blocked=False)

    def _check_capability_escalation(self, skill_md: str) -> ThreatResult:
        # MOCKED implementation
        return ThreatResult(category="CAPABILITY_ESCALATION", blocked=False)

    def _check_malicious_code(self, source_files: list[dict]) -> ThreatResult:
        for f in source_files:
            if f.get("ext") in [".py", ".js", ".ts", ".sh"]:
                result = subprocess.run(
                    [
                        "semgrep",
                        "--config=p/security-audit",
                        f["path"],
                        "--json",
                        "--timeout=30"
                    ],
                    capture_output=True,
                    timeout=60
                )
                findings = parse_semgrep_output(result.stdout)
                critical = [x for x in findings if x.get("severity") == "ERROR"]
                if critical:
                    return ThreatResult(
                        category="MALICIOUS_CODE",
                        blocked=True,
                        evidence=critical[0].get("message", "")
                    )
        return ThreatResult(category="MALICIOUS_CODE", blocked=False)

    def _check_supply_chain(self, dependencies: list[dict]) -> ThreatResult:
        """Queries OSV.dev for known CVEs in all absorbed dependencies."""
        for dep in dependencies:
            resp = httpx.post(self.OSV_API, json={
                "package": {"name": dep.get("name"), "ecosystem": dep.get("ecosystem")}
            })
            vulns = resp.json().get("vulns", [])
            critical = [v for v in vulns if v.get("severity") == "CRITICAL"]
            if critical:
                return ThreatResult(
                    category="SUPPLY_CHAIN",
                    blocked=True,
                    evidence=f"CVE {critical[0].get('id')} in {dep.get('name')}"
                )
        return ThreatResult(category="SUPPLY_CHAIN", blocked=False)

    def _check_network_scope(self, skill_md: str) -> ThreatResult:
        # MOCKED implementation
        return ThreatResult(category="NETWORK_SCOPE", blocked=False)