import logging
import os
import urllib.parse
import uuid
from pathlib import Path

import httpx
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from src.domain.arap.skill_parser import parse_skill_frontmatter, validate_skill_schema

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SkillRegistry")


def parse_skill_metadata(path: str) -> dict | None:
    skill_path = Path(path)
    if skill_path.name != "SKILL.md":
        logger.warning("Skipping non-SKILL file", extra={"skill_path": path})
        return None

    try:
        content = skill_path.read_text(encoding="utf-8")
        frontmatter = parse_skill_frontmatter(content)
        is_valid, errors = validate_skill_schema(frontmatter)
        if not is_valid:
            error_payload = {
                "file_path": path,
                "validation_errors": errors,
            }
            logger.error("Invalid SKILL.md schema", extra=error_payload)
            return {"error": error_payload}

        return {
            "name": frontmatter["name"],
            "version": frontmatter["version"],
            "description": frontmatter["description"],
            "path": path,
        }
    except Exception as exc:
        error_payload = {
            "file_path": path,
            "validation_errors": [str(exc)],
        }
        logger.error("Failed to parse SKILL.md", extra=error_payload)
        return {"error": error_payload}


class HiClawClient:
    def nacos_register(self, service_name: str, metadata: dict):
        query_params = urllib.parse.urlencode({
            "serviceName": service_name,
            "ip": "127.0.0.1",
            "port": 8000,
            "ephemeral": "false",
        })
        url = f"http://hiclaw-manager:18789/nacos/v1/ns/instance?{query_params}"
        try:
            httpx.post(url, json=metadata)
            logger.info(f"Registered {service_name} with Nacos")
        except Exception as e:
            logger.error(f"Failed to register with Nacos: {e}")


class MatrixClient:
    def __init__(self):
        self.access_token = os.getenv("MATRIX_ACCESS_TOKEN", "dummy_token")

    def send_to_room(self, room: str, message: str):
        room_id = urllib.parse.quote(room)
        txn_id = str(uuid.uuid4())
        url = f"http://tuwunel-matrix:8008/_matrix/client/v3/rooms/{room_id}/send/m.room.message/{txn_id}"

        headers = {"Authorization": f"Bearer {self.access_token}"}
        payload = {"msgtype": "m.text", "body": message}

        try:
            httpx.put(url, json=payload, headers=headers)
            logger.info(f"Sent Matrix notification to {room}")
        except Exception as e:
            logger.error(f"Failed to send Matrix notification: {e}")


class SkillHotReloader(FileSystemEventHandler):
    def __init__(self):
        self.hiclaw = HiClawClient()
        self.matrix = MatrixClient()

    def on_created(self, event):
        if event.src_path.endswith("SKILL.md"):
            self._reload_skill(event.src_path, "ADDED")

    def on_modified(self, event):
        if event.src_path.endswith("SKILL.md"):
            self._reload_skill(event.src_path, "UPDATED")

    def _reload_skill(self, path: str, action: str):
        metadata = parse_skill_metadata(path)
        if not metadata or metadata.get("error"):
            logger.warning("Skill skipped due to invalid metadata", extra={"skill_path": path, "action": action, "metadata": metadata})
            return

        self.hiclaw.nacos_register(
            service_name=f"skill.{metadata['name']}",
            metadata={"version": metadata["version"], "path": path, "action": action},
        )

        self.matrix.send_to_room(
            room="#skill-updates:daemon.local",
            message=f"🧠 Skill {action}: `{metadata['name']}` v{metadata['version']} — hot-reloaded",
        )


if __name__ == "__main__":
    event_handler = SkillHotReloader()
    observer = Observer()
    observer.schedule(event_handler, path="/var/lib/daemon/skills", recursive=True)
    observer.start()
    try:
        import time

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
