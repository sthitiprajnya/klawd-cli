import logging
import httpx
from abc import ABC, abstractmethod
from src.utils.nim_router import nim_router

logger = logging.getLogger("BaseAgent")

class BaseAgent(ABC):
    def __init__(self, name: str, role: str, system_prompt: str):
        self.name = name
        self.role = role
        self._fallback_prompt = system_prompt
        self._dynamic_prompt = None

    @property
    def system_prompt(self) -> str:
        if self._dynamic_prompt is None:
            self._dynamic_prompt = self._fetch_dynamic_prompt(self.role, self._fallback_prompt)
        return self._dynamic_prompt

    def _fetch_dynamic_prompt(self, role: str, fallback: str) -> str:
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "get_persona",
                "params": {"role": role},
                "id": 1
            }
            response = httpx.post("http://openhuman-core:7788/jsonrpc", json=payload, timeout=2.0)
            if response.status_code == 200:
                data = response.json()
                result = data.get("result")
                if result:
                    logger.info(f"Loaded dynamic persona for {role}")
                    return result
        except Exception as e:
            logger.warning(f"Failed to fetch dynamic prompt for {role}: {e}")
        logger.info(f"Using fallback prompt for {role}")
        return fallback

    def process(self, prompt: str, task_type: str = "coding") -> str:
        """
        Processes a prompt via the advanced router with this agent's system prompt.
        """
        logger.info(f"{self.name} ({self.role}) is processing task.")
        full_prompt = f"System: {self.system_prompt}\n\nUser: {prompt}"
        return nim_router.route_task(full_prompt, task_type=task_type)
