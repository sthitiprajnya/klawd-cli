import logging

from litellm.integrations.custom_logger import CustomLogger

logger = logging.getLogger("RoutingAuditor")


class RoutingViolation(Exception):
    pass


class RoutingAuditorHook(CustomLogger):
    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        model = kwargs.get("model", "unknown")
        metadata = kwargs.get("metadata", {})

        latency_ms = max((end_time - start_time).total_seconds() * 1000, 0.0)
        usage = getattr(response_obj, "usage", None)
        prompt_tokens = getattr(usage, "prompt_tokens", None)
        completion_tokens = getattr(usage, "completion_tokens", None)

        logger.info(
            "routing_decision",
            extra={
                "routing": {
                    "task_type": metadata.get("task_type"),
                    "job_id": metadata.get("job_id"),
                    "primary": metadata.get("primary_model", model),
                    "fallback": metadata.get("fallback_model"),
                    "selected": model,
                    "latency_ms": round(latency_ms, 2),
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "retry_count": metadata.get("retry_count", 0),
                }
            },
        )

    def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        self.log_success_event(kwargs, response_obj, start_time, end_time)
