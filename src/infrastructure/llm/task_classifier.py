import logging
from litellm.integrations.custom_logger import CustomLogger

logger = logging.getLogger("TaskClassifier")

class RoutingViolation(Exception):
    pass

ROUTING_RULES = [
    (["design", "architecture", "scope", "prd"], "nim-architect", "Architect"),
    (["absorb", "analyze repo"], "nim-architect", "X-Ray Analyst"),
    (["implement", "fix", "debug", "write", "bash"], "nim-coder", "Senior Engineer"),
    (["test", "pytest", "coverage"], "nim-coder", "QA Engineer"),
]

class TaskClassifierHook(CustomLogger):
    def log_pre_api_call(self, model, messages, kwargs):
        prompt = " ".join(m.get("content", "") for m in messages if isinstance(m.get("content"), str)).lower()
        matched_model, matched_score = None, 0

        for patterns, target_model, persona in ROUTING_RULES:
            hits = sum(1 for p in patterns if p in prompt)
            if hits > matched_score:
                matched_score, matched_model = hits, target_model

        if model == "nim-coder" and matched_model == "nim-architect" and matched_score >= 2:
            logger.error("Routing Violation: nim-architect task sent to nim-coder.")
            raise RoutingViolation("Task requires nim-architect but nim-coder requested. Halting.")
