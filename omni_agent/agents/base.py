import logging
from abc import ABC, abstractmethod
from omni_agent.utils.nim_router import nim_router

logger = logging.getLogger("BaseAgent")

class BaseAgent(ABC):
    def __init__(self, name: str, role: str, system_prompt: str):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt

    def process(self, prompt: str, task_type: str = "coding") -> str:
        """
        Processes a prompt via the advanced router with this agent's system prompt.
        """
        logger.info(f"{self.name} ({self.role}) is processing task.")
        full_prompt = f"System: {self.system_prompt}\n\nUser: {prompt}"
        return nim_router.route_task(full_prompt, task_type=task_type)
