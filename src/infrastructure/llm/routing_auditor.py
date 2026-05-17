import logging
from litellm.integrations.custom_logger import CustomLogger

logger = logging.getLogger("RoutingAuditor")

class RoutingViolation(Exception):
    pass

class RoutingAuditorHook(CustomLogger):
    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        """
        Validates model output against capability contracts.
        """
        model = kwargs.get("model", "unknown")

        if model == "nim-coder":
            try:
                if hasattr(response_obj, 'choices') and len(response_obj.choices) > 0:
                    content = response_obj.choices[0].message.content.lower()
                else:
                    content = ""
            except Exception:
                content = ""

            forbidden_keywords = ["architecture document", "adr", "master plan", "strategic roadmap"]
            for kw in forbidden_keywords:
                if kw in content:
                    logger.error(f"Routing Violation: {model} generated unauthorized content '{kw}'.")
                    raise RoutingViolation(f"Model contract violation: nim-coder generated unauthorized content '{kw}'.")

    def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        self.log_success_event(kwargs, response_obj, start_time, end_time)
