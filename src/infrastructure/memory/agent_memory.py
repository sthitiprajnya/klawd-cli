import hashlib
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
        logger.info("Initializing Memory manager connecting to JSON-RPC at %s.", self.base_url)

    @staticmethod
    def _utc_now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _build_idempotency_key(
        *,
        task: str,
        result: str,
        feedback: str,
        metadata: dict[str, Any],
        job_id: str | None,
        status: str,
        failure_class: str,
    ) -> str:
        canonical = {
            "job_id": job_id or metadata.get("job_id"),
            "task": task,
            "result": result,
            "feedback": feedback,
            "status": status,
            "failure_class": failure_class,
            "layer": metadata.get("layer", "unknown"),
            "domain": metadata.get("domain", "unknown"),
        }
        digest = hashlib.sha256(json.dumps(canonical, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
        return f"mem_{digest[:24]}"

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
        metadata: dict[str, Any] | None = None,
        *,
        job_id: str | None = None,
        agent: str = "workflow",
        status: str = "unknown",
        failure_class: str = "NONE",
        parent_id: str | None = None,
        related_ids: list[str] | None = None,
    ) -> str:
        """Stores workflow outcome using a unified record schema.

        Supports legacy `metadata` callers while also enabling structured fields.
        """
        meta = dict(metadata or {})
        if job_id is None:
            job_id = meta.get("job_id")

        record_id = self._build_idempotency_key(
            task=task,
            result=result,
            feedback=feedback,
            metadata=meta,
            job_id=job_id,
            status=status,
            failure_class=failure_class,
        )
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
                **meta,
            },
            "refs": {
                "parent_id": parent_id,
                "related_ids": related_ids or [],
            },
        }

        try:
            self._store_record(record)
            logger.info("Stored unified memory record with idempotency key %s.", record_id)
        except Exception as e:
            logger.error("Failed to store memory: %s", e)
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
            logger.warning("Retrieve failed: %s", e)
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
