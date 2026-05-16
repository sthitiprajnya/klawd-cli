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
        # Support up to 5 API keys passed as env vars API_KEY_1...5
        # Can be mixed between NVIDIA NIM, Zhipu (GLM), Moonshot (Kimi), Minimax
        self.api_keys = []
        for i in range(1, 6):
            key = os.getenv(f"API_KEY_{i}")
            if key:
                self.api_keys.append(key)

        if not self.api_keys:
            logger.warning("No API keys found in environment variables. Setting dummy key for mock testing.")
            self.api_keys = ["mock-key-1"]

        self.current_key_idx = 0

        # Mapping advanced models for specific tasks to achieve Claude-level capabilities
        self.MODELS = {
            "complex": "moonshot-v1-128k",   # Kimi model for extreme context/complex reasoning
            "coding": "glm-4-plus",          # GLM for robust coding capabilities (closest to GLM-5.1 if available)
            "fast": "minimax-text-01",       # Minimax for quick planning/routing
            "reflection": "meta/llama-3.1-405b-instruct" # NVIDIA NIM fallback/alternative
        }

    def _get_next_client(self, task_type: str) -> OpenAI:
        """Round-robin selection of API keys and dynamic base_url based on model/provider."""
        key = self.api_keys[self.current_key_idx]
        self.current_key_idx = (self.current_key_idx + 1) % len(self.api_keys)

        # Determine the base URL based on the task/model target
        # In a real environment, you'd map specific keys to specific providers.
        # Here we demonstrate the routing infrastructure.
        base_url = "https://integrate.api.nvidia.com/v1" # Default NIM

        if task_type == "coding":
            base_url = "https://open.bigmodel.cn/api/paas/v4" # Zhipu/GLM
        elif task_type == "complex":
            base_url = "https://api.moonshot.cn/v1" # Moonshot/Kimi
        elif task_type == "fast":
            base_url = "https://api.minimax.chat/v1" # Minimax

        return OpenAI(
            api_key=key,
            base_url=base_url
        )

    def route_task(self, prompt: str, task_type: str = "coding") -> str:
        """
        Intelligently routes a prompt to Kimi, GLM, Minimax, or NIM based on task.
        """
        model = self.MODELS.get(task_type, self.MODELS["coding"])

        # Fallback for extremely large prompts requiring Kimi's context window
        if len(prompt) > 8000 and task_type != "complex":
            logger.info(f"Prompt length {len(prompt)} exceeds threshold. Upgrading to Kimi (complex model).")
            model = self.MODELS["complex"]
            task_type = "complex"

        logger.info(f"Routing task to model {model} via provider for {task_type}")

        client = self._get_next_client(task_type)

        if self.api_keys[0].startswith("mock-"):
            return f"[MOCK RESPONSE from {model}] Processed: {prompt[:50]}..."

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=4096,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling API for {model}: {str(e)}")
            return f"Error: {str(e)}"

# Singleton instance
nim_router = NIMRouter()
