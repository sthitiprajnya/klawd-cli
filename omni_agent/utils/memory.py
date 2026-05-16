import logging
from typing import Dict, List, Any
import sqlite3

logger = logging.getLogger("Memory")

class AgentMemory:
    def __init__(self, index_name: str = "omni_agent_memory"):
        self.index_name = index_name
        self.db_path = "mempalace_mock.db"
        logger.info("Initializing Memory manager (Persistent SQLite mimicking MemPalace).")
        self._init_db()

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS memory_entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        task TEXT,
                        result TEXT,
                        feedback TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to init DB: {e}")

    def store_outcome(self, task: str, result: str, feedback: str) -> None:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO memory_entries (task, result, feedback) VALUES (?, ?, ?)",
                    (task, result, feedback)
                )
                conn.commit()
            logger.info("Successfully stored task outcome in Memory.")
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")

    def retrieve_lessons(self, context: str) -> str:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT task, result, feedback FROM memory_entries ORDER BY id DESC LIMIT 5"
                )
                rows = cursor.fetchall()

            if not rows:
                return "No past lessons found."

            lessons = [f"Task: {row[0]}\nResult: {row[1]}\nFeedback: {row[2]}" for row in rows]
            return "\n---\n".join(lessons)
        except Exception as e:
            logger.warning(f"Retrieve failed: {e}")
            return "Could not retrieve past lessons."

agent_memory = AgentMemory()
