import logging
import httpx
from abc import ABC, abstractmethod
from src.infrastructure.llm_router import llm_router

logger = logging.getLogger("BaseAgent")

class BaseAgent(ABC):
    def __init__(self, name: str, role: str, system_prompt: str):
        self.name = name
        self.role = role
        self.base_system_prompt = system_prompt
        self.openhuman_url = "http://openhuman-core:7788/jsonrpc"

    def _get_dynamic_context(self) -> str:
        """Fetches dynamic context from OpenHuman memory trees."""
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "get_global_context",
                "params": {},
                "id": 1
            }
            response = httpx.post(self.openhuman_url, json=payload, timeout=2.0)
            if response.status_code == 200:
                data = response.json()
                if "result" in data and data["result"]:
                    return f"\n[Dynamic Global Context from OpenHuman: {data['result']}]"
        except Exception as e:
            logger.debug(f"Failed to fetch dynamic context from OpenHuman: {e}")

        return ""

    def process(self, prompt: str, task_type: str = "coding") -> str:
        """
        Processes a prompt via the advanced router with this agent's dynamic system prompt.
        """
        logger.info(f"{self.name} ({self.role}) is processing task.")
        dynamic_context = self._get_dynamic_context()
        full_system_prompt = f"{self.base_system_prompt}{dynamic_context}"

        full_prompt = f"System: {full_system_prompt}\n\nUser: {prompt}"
        return llm_router.route(full_prompt, task_type=task_type)
