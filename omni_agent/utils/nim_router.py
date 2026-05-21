import os
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
        # We now rely purely on LiteLLM proxy for load balancing and key management
        self.base_url = "http://litellm-proxy:4000/v1"
        self.api_key = "dummy-key" # litellm doesn't need a real key if configured internally

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        # Mapping logical task types to Litellm router models
        self.MODELS = {
            "complex": "nim-architect",
            "coding": "nim-coder",
            "fast": "nim-coder", # fallback to coder for fast tasks if needed
            "reflection": "nim-architect"
        }

    def route_task(self, prompt: str, task_type: str = "coding") -> str:
        """
        Intelligently routes a prompt through litellm-proxy based on task.
        """
        model = self.MODELS.get(task_type, self.MODELS["coding"])

        if len(prompt) > 8000 and task_type != "complex":
            logger.info(f"Prompt length {len(prompt)} exceeds threshold. Upgrading to architect model.")
            model = self.MODELS["complex"]
            task_type = "complex"

        logger.info(f"Routing task via litellm-proxy to model {model} for {task_type}")

        try:
            # We pass task_type in extra_body so Litellm pre_call hooks can use it
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=4096,
                extra_body={"metadata": {"task_type": task_type}}
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling litellm-proxy for {model}: {str(e)}")
            return f"Error: {str(e)}"

# Singleton instance
nim_router = NIMRouter()
