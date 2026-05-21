import logging
from datetime import datetime

logger = logging.getLogger("OmniAgentMemory")

class AgentMemory:
    def __init__(self, index_name: str = "omni_agent_memory"):
        self.index_name = index_name
        logger.info(f"Initializing Memory manager (Mocked MemPalace backend integration).")
        self.mock_db = []

    def store_outcome(self, task: str, result: str, feedback: str) -> str:
        record_id = f"mem_{len(self.mock_db)}"
        record = {
            "id": record_id,
            "task": task,
            "result": result,
            "feedback": feedback,
            "timestamp": datetime.now().isoformat()
        }
        self.mock_db.append(record)
        return record_id

    def retrieve_lessons(self, context: str, top_k: int = 3) -> str:
        if not self.mock_db:
            return "No past lessons found."

        # Mock behavior: return the most recent entries matching the context loosely (or all if short)
        lessons = []
        for record in reversed(self.mock_db):
            if context.lower() in record["task"].lower() or context.lower() in record["result"].lower():
                lessons.append(record)
                if len(lessons) >= top_k:
                    break

        if not lessons:
            return "No past lessons found."

        # Format lessons
        formatted = []
        for l in lessons:
            formatted.append(f"Task: {l['task']}\nResult: {l['result']}\nFeedback: {l['feedback']}")

        return "\n---\n".join(formatted)
