import logging
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
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")

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
            return "No past lessons found."
        except Exception as e:
            logger.warning(f"Retrieve failed: {e}")
            return "Could not retrieve past lessons."

agent_memory = AgentMemory()
