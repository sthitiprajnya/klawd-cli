import logging

logger = logging.getLogger("Memory")

class AgentMemory:
    def __init__(self, index_name: str = "omni_agent_memory"):
        self.index_name = index_name
        logger.info(f"Initializing Memory manager (Mocked MemPalace backend integration).")
        self.mock_db = []

    def store_outcome(self, task: str, result: str, feedback: str):
        """Stores the result of a task and any feedback for future reference."""
        try:
            content = f"Task: {task}\nResult: {result}\nFeedback: {feedback}"
            self.mock_db.append(content)
            logger.info("Successfully stored task outcome in Memory.")
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")

    def retrieve_lessons(self, context: str) -> str:
        """Retrieves past lessons related to the current context."""
        try:
            if not self.mock_db:
                return "No past lessons found."
            return "\n---\n".join(self.mock_db[-3:])
        except Exception as e:
            logger.warning(f"Retrieve failed: {e}")
            return "Could not retrieve past lessons."

agent_memory = AgentMemory()
