import logging
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LLMRouter")

class LLMRouter:
    def __init__(self):
        # Rely purely on LiteLLM proxy for load balancing and deterministic routing
        self.base_url = "http://litellm-proxy:4000/v1"
        self.api_key = "dummy-key" # LiteLLM manages the real NIM keys internally

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def route(self, prompt: str, task_type: str = "coding") -> str:
        logger.info(f"Routing task via litellm-proxy for {task_type}")

        try:
            # We pass task_type in extra_body so LiteLLM pre_call hooks (task_classifier.py) can intercept it
            response = self.client.chat.completions.create(
                model="nim-coder", # Default fallback, classifier will override if needed
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=4096,
                extra_body={"metadata": {"task_type": task_type}}
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling litellm-proxy: {str(e)}")
            return f"Error: {str(e)}"

llm_router = LLMRouter()
