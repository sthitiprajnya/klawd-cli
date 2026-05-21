import logging
import os
from pathlib import Path
from typing import Any

from openai import OpenAI

logger = logging.getLogger("LLMRouter")


class LLMRouter:
    def __init__(self):
        self.base_url = os.getenv("LITELLM_PROXY_BASE_URL", "http://litellm-proxy:4000/v1")
        self.api_keys = self._load_api_keys()
        self._validate_litellm_config()
        self.clients = [OpenAI(api_key=key, base_url=self.base_url) for key in self.api_keys]
        self._next_client_idx = 0
        self.MODELS = {
            "complex": "nim-architect",
            "coding": "nim-coder",
            "fast": "nim-coder",
            "reflection": "nim-architect",
        }

    def _load_api_keys(self) -> list[str]:
        keys: list[str] = []
        single_key = os.getenv("LITELLM_API_KEY")
        if single_key:
            keys.append(single_key)

        multi_key_raw = os.getenv("NIM_API_KEYS", "")
        if multi_key_raw.strip():
            keys.extend([k.strip() for k in multi_key_raw.split(",") if k.strip()])

        if not keys:
            keys = ["dummy-key"]
        return list(dict.fromkeys(keys))

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
        missing_models = [m.split(": ", 1)[1] for m in required_models if m not in raw]
        if missing_models:
            raise ValueError(f"LiteLLM config missing routed models: {missing_models}")

    def _iter_clients(self):
        count = len(self.clients)
        for offset in range(count):
            idx = (self._next_client_idx + offset) % count
            yield idx, self.clients[idx]

    def route(self, prompt: str, task_type: str = "coding", job_id: str | None = None, token_budget: int = 4096, system_prompt: str | None = None) -> str:
        model = self.MODELS.get(task_type, self.MODELS["coding"])

        total_length = len(prompt) + (len(system_prompt) if system_prompt else 0)

        if total_length > 8000 and task_type != "complex":
            logger.info("Prompt length %s exceeds threshold. Upgrading to architect model.", total_length)
            model = self.MODELS["complex"]
            task_type = "complex"

        metadata: dict[str, Any] = {
            "task_type": task_type,
            "job_id": job_id,
            "token_budget": token_budget,
            "prompt_chars": total_length,
            "api_key_pool_size": len(self.clients),
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        failures: list[str] = []
        for idx, client in self._iter_clients():
            logger.info("Routing task via litellm-proxy to model=%s task=%s key_slot=%s", model, task_type, idx)
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.2,
                    max_tokens=token_budget,
                    extra_body={"metadata": metadata},
                )
                self._next_client_idx = (idx + 1) % len(self.clients)
                return response.choices[0].message.content
            except Exception as e:
                reason = f"slot={idx}:{str(e)}"
                failures.append(reason)
                logger.warning("LLM call failed (%s), attempting failover.", reason)

        logger.error("All failover paths exhausted for model %s. failures=%s", model, failures)
        return "Error: all model routes failed after failover attempts"


llm_router = LLMRouter()
