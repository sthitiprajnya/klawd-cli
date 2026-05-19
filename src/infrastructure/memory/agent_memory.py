import json
import logging
from datetime import datetime, timezone
from typing import Any

import httpx

logger = logging.getLogger("Memory")


class AgentMemory:
    def __init__(self, index_name: str = "src_memory"):
        self.index_name = index_name
        self.base_url = "http://agentmemory:3111"
        logger.info(f"Initializing Memory manager connecting to JSON-RPC at {self.base_url}.")

    def store_outcome(self, task: str, result: str, feedback: str, metadata: dict | None = None):
        """Stores the result of a task and any feedback for future reference."""
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "store_outcome",
                "params": {"task": task, "result": result, "feedback": feedback, "metadata": metadata or {}},
                "id": 1
            }
            httpx.post(self.base_url, json=payload, timeout=2.0)
            logger.info("Successfully stored task outcome in Memory.")
    @staticmethod
    def _utc_now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _store_record(self, record: dict[str, Any]) -> None:
        payload = {
            "jsonrpc": "2.0",
            "method": "memory_save",
            "params": {"content": json.dumps(record)},
            "id": 1,
        }
        httpx.post(self.base_url, json=payload, timeout=2.0)

    def store_outcome(
        self,
        task: str,
        result: str,
        feedback: str,
        *,
        job_id: str | None = None,
        agent: str = "workflow",
        status: str = "unknown",
        failure_class: str = "NONE",
        parent_id: str | None = None,
        related_ids: list[str] | None = None,
    ) -> str:
        """Stores workflow outcome using a unified record schema."""
        record_id = f"mem_{int(datetime.now(timezone.utc).timestamp() * 1000000)}"
        timestamp = self._utc_now_iso()
        record = {
            "id": record_id,
            "type": "workflow_outcome",
            "content": {
                "task": task,
                "result": result,
                "feedback": feedback,
            },
            "metadata": {
                "job_id": job_id,
                "agent": agent,
                "status": status,
                "failure_class": failure_class,
                "created_at": timestamp,
                "updated_at": timestamp,
            },
            "refs": {
                "parent_id": parent_id,
                "related_ids": related_ids or [],
            },
        }

        try:
            self._store_record(record)
            logger.info("Successfully stored unified memory record.")
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
        return record_id

    def _search_records(self, query: str) -> list[dict[str, Any]]:
        payload = {
            "jsonrpc": "2.0",
            "method": "memory_smart_search",
            "params": {"query": query},
            "id": 1,
        }
        response = httpx.post(self.base_url, json=payload, timeout=2.0)
        if response.status_code != 200:
            return []

        result = response.json().get("result", [])
        if isinstance(result, str):
            result = [result]
        parsed: list[dict[str, Any]] = []
        for item in result:
            if isinstance(item, dict):
                parsed.append(item)
                continue
            if isinstance(item, str):
                try:
                    parsed.append(json.loads(item))
                except json.JSONDecodeError:
                    continue
        return parsed

    def retrieve_lessons(self, context: str, top_k: int = 3) -> str:
        """Retrieves past lessons related to the current context."""
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "retrieve_lessons",
                "params": {"context": context, "top_k": top_k},
                "id": 1
            }
            response = httpx.post(self.base_url, json=payload, timeout=2.0)
            if response.status_code == 200:
                data = response.json()
                if "result" in data and data["result"]:
                    if isinstance(data["result"], list):
                        return "\n---\n".join(data["result"][-3:])
                    return str(data["result"])
            records = self._search_records(context)
            if records:
                snippets = [json.dumps(r.get("content", r), default=str) for r in records[-3:]]
                return "\n---\n".join(snippets)
            return "No past lessons found."
        except Exception as e:
            logger.warning(f"Retrieve failed: {e}")
            return "Could not retrieve past lessons."

    def last_failures_by_class(self, failure_class: str, limit: int = 5) -> list[dict[str, Any]]:
        records = self._search_records(f"type:workflow_outcome failure_class:{failure_class}")
        filtered = [r for r in records if r.get("metadata", {}).get("failure_class") == failure_class]
        filtered.sort(key=lambda r: r.get("metadata", {}).get("updated_at", ""), reverse=True)
        return filtered[:limit]

    def top_similar_lessons_by_task_domain(self, task_domain: str, limit: int = 5) -> list[dict[str, Any]]:
        records = self._search_records(f"type:workflow_outcome domain:{task_domain}")
        filtered = [
            r
            for r in records
            if task_domain.lower() in str(r.get("content", {}).get("task", "")).lower()
        ]
        return filtered[:limit]


agent_memory = AgentMemory()
