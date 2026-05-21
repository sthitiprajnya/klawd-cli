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
