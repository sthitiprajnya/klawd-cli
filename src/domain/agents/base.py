import logging
import os
import time
from abc import ABC
from typing import Any, TypedDict

import httpx

from src.infrastructure.llm_router import llm_router
from src.infrastructure.security.execution_adapter import execution_adapter

logger = logging.getLogger("BaseAgent")


class OpenHumanJsonRpcResult(TypedDict, total=False):
    context: str
    status: str


class OpenHumanJsonRpcResponse(TypedDict, total=False):
    jsonrpc: str
    id: int | str | None
    result: OpenHumanJsonRpcResult | str
    error: dict[str, Any]


class BaseAgent(ABC):
    def __init__(self, name: str, role: str, system_prompt: str):
        self.name = name
        self.role = role
        self.base_system_prompt = system_prompt
        self.openhuman_url = os.getenv("OPENHUMAN_JSONRPC_URL", "http://openhuman-core:7788/jsonrpc")
        self.openhuman_timeout_seconds = float(os.getenv("OPENHUMAN_TIMEOUT_SECONDS", "2.0"))
        self.openhuman_max_retries = int(os.getenv("OPENHUMAN_MAX_RETRIES", "1"))
        self.last_openhuman_observability: dict[str, Any] = {
            "openhuman_available": False,
            "openhuman_latency_ms": None,
            "openhuman_error": "not_attempted",
        }

    @staticmethod
    def _extract_context(payload: OpenHumanJsonRpcResponse) -> str | None:
        """Adapter for expected OpenHuman JSON-RPC shapes.

        Expected shapes:
        - memory_tree.get => {"result": {"context": "..."}}
        - prompt.update => {"result": "..."}
        """
        result = payload.get("result")
        if isinstance(result, dict):
            context_value = result.get("context")
            if isinstance(context_value, str) and context_value.strip():
                return context_value
        elif isinstance(result, str) and result.strip():
            return result
        return None

    def _get_dynamic_context(self) -> str:
        """Fetch dynamic context from OpenHuman with timeout/retry/fallback semantics."""
        last_error = "unknown_error"
        attempts = self.openhuman_max_retries + 1

        for attempt in range(1, attempts + 1):
            start = time.perf_counter()
            try:
                payload = {
                    "jsonrpc": "2.0",
                    "method": "memory_tree.get",
                    "params": {"key": "global_context"},
                    "id": 1,
                }
                response = httpx.post(self.openhuman_url, json=payload, timeout=self.openhuman_timeout_seconds)
                latency_ms = round((time.perf_counter() - start) * 1000, 2)

                if response.status_code != 200:
                    last_error = f"http_{response.status_code}"
                    continue

                data: OpenHumanJsonRpcResponse = response.json()
                context = self._extract_context(data)
                if context:
                    self.last_openhuman_observability = {
                        "openhuman_available": True,
                        "openhuman_latency_ms": latency_ms,
                        "openhuman_error": None,
                        "openhuman_attempts": attempt,
                    }
                    return f"\n[Dynamic Global Context from OpenHuman: {context}]"

                last_error = "malformed_jsonrpc_payload"
            except httpx.TimeoutException:
                last_error = "timeout"
            except Exception as e:
                last_error = f"exception:{type(e).__name__}"
                logger.debug("Failed to fetch dynamic context from OpenHuman: %s", e)

        self.last_openhuman_observability = {
            "openhuman_available": False,
            "openhuman_latency_ms": None,
            "openhuman_error": last_error,
            "openhuman_attempts": attempts,
        }
        return "\n[Context: Stateless fallback mode enabled (OpenHuman unavailable)]"

    def process(self, prompt: str, task_type: str = "coding") -> str:
        logger.info(f"{self.name} ({self.role}) is processing task.")
        dynamic_context = self._get_dynamic_context()
        full_system_prompt = f"{self.base_system_prompt}{dynamic_context}"

        full_prompt = f"System: {full_system_prompt}\n\nUser: {prompt}"
        execution_adapter.execute(prompt=full_prompt, task_type=task_type, command=prompt)
        return llm_router.route(prompt, task_type=task_type, system_prompt=full_system_prompt)
