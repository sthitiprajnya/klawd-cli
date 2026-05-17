class RoutingViolation(Exception):
    pass

class CustomLogger:
    pass

class RoutingAuditorHook(CustomLogger):
    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        """
        Validates model output against capability contracts.
        """
        model = kwargs.get("model", "unknown")

        if model == "nim-coder":
            try:
                # LiteLLM passes standard openai response objects or dicts
                if hasattr(response_obj, 'choices') and len(response_obj.choices) > 0:
                    content = response_obj.choices[0].message.content.lower()
                else:
                    content = ""
            except Exception:
                content = ""

            forbidden_keywords = ["architecture document", "adr", "master plan"]
            for kw in forbidden_keywords:
                if kw in content:
                    raise RoutingViolation(f"Model contract violation: nim-coder generated unauthorized content '{kw}'.")

    def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        self.log_success_event(kwargs, response_obj, start_time, end_time)