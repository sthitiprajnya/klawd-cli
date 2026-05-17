import os
import logging
from typing import Dict
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("LLMRouter")

class LLMRouter:
    def __init__(self):
        self.api_keys = [os.getenv(f"NIM_API_KEY_{i}") for i in range(1, 6) if os.getenv(f"NIM_API_KEY_{i}")]
        if not self.api_keys:
            logger.warning("No API keys found. Using mock fallback.")
            self.api_keys = ["mock-key-1"]

        self.current_key_idx = 0

        self.MODELS = {
            "complex": "moonshot-v1-128k",
            "coding": "glm-4-plus",
            "fast": "minimax-text-01",
            "reflection": "glm-4-plus"
        }

    def _get_client(self, task_type: str) -> OpenAI:
        key = self.api_keys[self.current_key_idx]
        self.current_key_idx = (self.current_key_idx + 1) % len(self.api_keys)

        base_url = "https://integrate.api.nvidia.com/v1"
        if task_type in ["coding", "reflection"]:
            base_url = "https://open.bigmodel.cn/api/paas/v4"
        elif task_type == "complex":
            base_url = "https://api.moonshot.cn/v1"
        elif task_type == "fast":
            base_url = "https://api.minimax.chat/v1"

        return OpenAI(api_key=key, base_url=base_url)

    def route(self, prompt: str, task_type: str = "coding") -> str:
        model = self.MODELS.get(task_type, self.MODELS["coding"])

        if len(prompt) > 8000 and task_type != "complex":
            model = self.MODELS["complex"]
            task_type = "complex"

        if self.api_keys[0].startswith("mock-"):
            if "Majin Buu" in prompt:
                return "```python\ndef absorbed_skill():\n    return 'Absorbed capability.'\n```"
            return f"[MOCK] Processed: {prompt[:30]}..."

        try:
            client = self._get_client(task_type)
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=4096,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"API Error for {model}: {e}")
            return f"Error: {e}"

llm_router = LLMRouter()
