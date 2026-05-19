import logging
from pathlib import Path
from typing import Any

from openai import OpenAI

logger = logging.getLogger("LLMRouter")


class LLMRouter:
    def __init__(self):
        self.base_url = "http://litellm-proxy:4000/v1"
        self.api_key = "dummy-key"
        self._validate_litellm_config()
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.MODELS = {
            "complex": "nim-architect",
            "coding": "nim-coder",
            "fast": "nim-coder",
            "reflection": "nim-architect",
        }

    def _validate_litellm_config(self, path: str = "litellm_config.yaml") -> None:
        cfg_path = Path(path)
        if not cfg_path.exists():
            raise ValueError(f"LiteLLM config missing: {path}")
        raw = cfg_path.read_text()
        required_top = ("model_list:", "router_settings:", "litellm_settings:")
        missing = [k.rstrip(":") for k in required_top if k not in raw]
        if missing:
            raise ValueError(f"LiteLLM config missing keys: {missing}")

        required_models = ("model_name: nim-architect", "model_name: nim-coder")
        missing_models = [m.split(": ",1)[1] for m in required_models if m not in raw]
        if missing_models:
            raise ValueError(f"LiteLLM config missing routed models: {missing_models}")

    def route(self, prompt: str, task_type: str = "coding", job_id: str | None = None, token_budget: int = 4096) -> str:
        model = self.MODELS.get(task_type, self.MODELS["coding"])

        if len(prompt) > 8000 and task_type != "complex":
            logger.info(f"Prompt length {len(prompt)} exceeds threshold. Upgrading to architect model.")
            model = self.MODELS["complex"]
            task_type = "complex"

        logger.info(f"Routing task via litellm-proxy to model {model} for {task_type}")
        metadata: dict[str, Any] = {
            "task_type": task_type,
            "job_id": job_id,
            "token_budget": token_budget,
            "prompt_chars": len(prompt),
        }

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=token_budget,
                extra_body={"metadata": metadata},
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling litellm-proxy for {model}: {str(e)}")
            return f"Error: {str(e)}"


llm_router = LLMRouter()
