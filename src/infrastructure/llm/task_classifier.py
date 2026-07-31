import logging
from dataclasses import dataclass

from litellm.integrations.custom_logger import CustomLogger

logger = logging.getLogger("TaskClassifier")


class RoutingViolation(Exception):
    pass


@dataclass(frozen=True)
class TaskRoute:
    task_class: str
    patterns: tuple[str, ...]
    primary_model: str
    fallback_model: str
    persona: str


TASK_ROUTES: tuple[TaskRoute, ...] = (
    TaskRoute("planning", ("design", "architecture", "scope", "prd"), "nim-architect", "nim-coder", "Architect"),
    TaskRoute("analysis", ("absorb", "analyze repo"), "nim-architect", "nim-coder", "X-Ray Analyst"),
    TaskRoute("implementation", ("implement", "fix", "debug", "write", "bash"), "nim-coder", "nim-architect", "Senior Engineer"),
    TaskRoute("validation", ("test", "pytest", "coverage"), "nim-coder", "nim-architect", "QA Engineer"),
)

TASK_ROUTE_INDEX: dict[str, TaskRoute] = {route.task_class: route for route in TASK_ROUTES}
DEFAULT_TASK_CLASS = "implementation"


def classify_task(prompt: str) -> TaskRoute:
    lowered = prompt.lower()
    best: tuple[int, TaskRoute] | None = None
    for route in TASK_ROUTES:
        hits = sum(1 for token in route.patterns if token in lowered)
        if hits <= 0:
            continue
        if best is None or hits > best[0]:
            best = (hits, route)
    return best[1] if best else TASK_ROUTE_INDEX[DEFAULT_TASK_CLASS]


class TaskClassifierHook(CustomLogger):
    def log_pre_api_call(self, model, messages, kwargs):
        prompt = " ".join(m.get("content", "") for m in messages if isinstance(m.get("content"), str))
        route = classify_task(prompt)

        metadata = kwargs.setdefault("metadata", {})
        metadata.setdefault("task_type", route.task_class)
        metadata.setdefault("primary_model", route.primary_model)
        metadata.setdefault("fallback_model", route.fallback_model)

        if model == "nim-coder" and route.primary_model == "nim-architect":
            logger.error("Routing Violation: nim-architect task sent to nim-coder.")
            raise RoutingViolation("Task requires nim-architect but nim-coder requested. Halting.")
