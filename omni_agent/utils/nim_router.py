import os
import random
import logging
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Setup basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("NIMRouter")

class NIMRouter:
    def __init__(self):
        # Support up to 5 NIM API keys passed as env vars NIM_API_KEY_1...5
        self.api_keys = []
        for i in range(1, 6):
            key = os.getenv(f"NIM_API_KEY_{i}")
            if key:
                self.api_keys.append(key)

        if not self.api_keys:
            logger.warning("No NIM API keys found in environment variables. Setting dummy key for mock testing.")
            self.api_keys = ["mock-key-1"]

        self.current_key_idx = 0

        # Mapping models for tasks
        self.MODELS = {
            "complex": "meta/llama-3.1-405b-instruct", # Complex reasoning/architecture
            "coding": "meta/llama-3.1-70b-instruct",   # Code generation
            "fast": "meta/llama-3.1-8b-instruct",      # Fast routing/summarization
        }

    def _get_next_client(self) -> OpenAI:
        """Round-robin selection of API keys to load-balance across the 5 keys."""
        key = self.api_keys[self.current_key_idx]
        self.current_key_idx = (self.current_key_idx + 1) % len(self.api_keys)

        # NVIDIA NIM API base URL
        return OpenAI(
            api_key=key,
            base_url="https://integrate.api.nvidia.com/v1"
        )

    def route_task(self, prompt: str, task_type: str = "coding") -> str:
        """
        Intelligently routes a prompt to an appropriate model.
        In a real implementation, it might calculate prompt complexity.
        """
        model = self.MODELS.get(task_type, self.MODELS["coding"])

        # Fast approximation for complexity fallback
        if len(prompt) > 4000 and task_type != "complex":
            logger.info(f"Prompt length {len(prompt)} exceeds threshold. Upgrading to complex model.")
            model = self.MODELS["complex"]

        logger.info(f"Routing task to model {model}")

        client = self._get_next_client()

        # Simple mock response for tests without keys, actual call otherwise
        if self.api_keys[0].startswith("mock-"):
            return f"[MOCK RESPONSE from {model}] Processed: {prompt[:50]}..."

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=2048,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling NIM API: {str(e)}")
            return f"Error: {str(e)}"

# Singleton instance
nim_router = NIMRouter()
