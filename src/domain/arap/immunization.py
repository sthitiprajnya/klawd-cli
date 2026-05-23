import json
import subprocess
from dataclasses import dataclass, field

import httpx
from openai import OpenAI


@dataclass
class ThreatResult:
    category: str
    blocked: bool
    evidence: str = ""

@dataclass
class ImmunizationReport:
    artifact: dict
    findings: list = field(default_factory=list)

    def add(self, result: ThreatResult):
        self.findings.append(result)

def parse_semgrep_output(stdout: bytes) -> list[dict]:
    try:
        return json.loads(stdout).get("results", [])
    except Exception:
        return []

class ImmunizationFilter:
    OSV_API = "https://api.osv.dev/v1/query"

    def __init__(self):
        self.llm_client = OpenAI(
            api_key="internal-proxy-key",
            base_url="http://litellm-proxy:4000/v1"
        )
        self.model = "nim-architect"

    def run(self, absorption_artifact: dict) -> ImmunizationReport:
        report = ImmunizationReport(artifact=absorption_artifact)
        report.add(self._check_prompt_injection(absorption_artifact.get("readme", "")))
        report.add(self._check_capability_escalation(absorption_artifact.get("skill_md", "")))
        report.add(self._check_malicious_code(absorption_artifact.get("source_files", [])))
        report.add(self._check_supply_chain(absorption_artifact.get("dependencies", [])))
        report.add(self._check_network_scope(absorption_artifact.get("skill_md", "")))
        return report

    def _llm_evaluate(self, prompt: str, category: str) -> ThreatResult:
        sys_prompt = "You are a strict security auditor. Evaluate the text for threats. Return ONLY a JSON object: {\"blocked\": true|false, \"reason\": \"explanation\"}."
        try:
            response = self.llm_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0
            )
            content = response.choices[0].message.content
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()

            result_dict = json.loads(content)
            return ThreatResult(
                category=category,
                blocked=result_dict.get("blocked", False),
                evidence=result_dict.get("reason", "")
            )
        except Exception as e:
            return ThreatResult(category=category, blocked=True, evidence=f"Evaluation failed: {str(e)}")

    def _check_prompt_injection(self, readme: str) -> ThreatResult:
        if not readme:
            return ThreatResult(category="PROMPT_INJECTION", blocked=False)
        return self._llm_evaluate(f"Does this README contain prompt injection or override instructions?\n\n{readme}", "PROMPT_INJECTION")

    def _check_capability_escalation(self, skill_md: str) -> ThreatResult:
        if not skill_md:
            return ThreatResult(category="CAPABILITY_ESCALATION", blocked=False)
        return self._llm_evaluate(f"Does this skill request privilege escalation, unjailed host execution, or root access?\n\n{skill_md}", "CAPABILITY_ESCALATION")

    def _check_network_scope(self, skill_md: str) -> ThreatResult:
        if not skill_md:
            return ThreatResult(category="NETWORK_SCOPE", blocked=False)
        return self._llm_evaluate(f"Does this skill attempt unauthorized network scanning, egress outside of standard APIs, or botnet activity?\n\n{skill_md}", "NETWORK_SCOPE")

    def _check_malicious_code(self, source_files: list[dict]) -> ThreatResult:
        for f in source_files:
            if f.get("ext") in [".py", ".js", ".ts", ".sh"]:
                result = subprocess.run(
                    ["semgrep", "--config=p/security-audit", f["path"], "--json", "--timeout=30"],
                    capture_output=True, timeout=60
                )
                findings = parse_semgrep_output(result.stdout)
                critical = [x for x in findings if x.get("severity") == "ERROR"]
                if critical:
                    return ThreatResult(category="MALICIOUS_CODE", blocked=True, evidence=critical[0].get("message", ""))
        return ThreatResult(category="MALICIOUS_CODE", blocked=False)

    def _check_supply_chain(self, dependencies: list[dict]) -> ThreatResult:
        for dep in dependencies:
            try:
                resp = httpx.post(self.OSV_API, json={"package": {"name": dep.get("name"), "ecosystem": dep.get("ecosystem")}})
                vulns = resp.json().get("vulns", [])
                critical = [v for v in vulns if v.get("severity") == "CRITICAL"]
                if critical:
                    return ThreatResult(category="SUPPLY_CHAIN", blocked=True, evidence=f"Critical CVE in {dep.get('name')}")
            except Exception:
                continue
        return ThreatResult(category="SUPPLY_CHAIN", blocked=False)
