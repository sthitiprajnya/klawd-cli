import logging
import httpx

logger = logging.getLogger("Memory")

class AgentMemory:
    def __init__(self, index_name: str = "src_memory"):
        self.index_name = index_name
        self.base_url = "http://agentmemory:3111"
        logger.info(f"Initializing Memory manager (AgentMemory backend integration).")

    def store_outcome(self, task: str, result: str, feedback: str):
        """Stores the result of a task and any feedback for future reference."""
        try:
            content = f"Task: {task}\nResult: {result}\nFeedback: {feedback}"
            payload = {
                "jsonrpc": "2.0",
                "method": "store_memory",
                "params": {"index": self.index_name, "content": content},
                "id": 1
            }
            response = httpx.post(self.base_url, json=payload, timeout=5.0)
            if response.status_code == 200:
                logger.info("Successfully stored task outcome in Memory.")
            else:
                logger.error(f"Failed to store memory: HTTP {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")

    def retrieve_lessons(self, context: str) -> str:
        """Retrieves past lessons related to the current context."""
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "retrieve_memory",
                "params": {"index": self.index_name, "context": context, "limit": 3},
                "id": 2
            }
            response = httpx.post(self.base_url, json=payload, timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                results = data.get("result", [])
                if not results:
                    return "No past lessons found."
                return "\n---\n".join(results)
            else:
                logger.warning(f"Retrieve failed: HTTP {response.status_code}")
                return "Could not retrieve past lessons."
        except Exception as e:
            logger.warning(f"Retrieve failed: {e}")
            return "Could not retrieve past lessons."

agent_memory = AgentMemory()
