import logging
import os
import time
import urllib.parse
import uuid
from pathlib import Path

import httpx
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from src.infrastructure.registry.skill_adapters import SkillAdapterRegistry, SkillProvenanceManifest, adapt_and_validate

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SkillRegistry")


def parse_skill_metadata(path: str, adapter_type: str | None = None, repo: str = "local") -> dict | None:
    skill_path = Path(path)
    if adapter_type is None and skill_path.name != "SKILL.md":
        logger.warning("Skipping non-SKILL file", extra={"skill_path": path})
        return None

    adapters = SkillAdapterRegistry()
    provenance = SkillProvenanceManifest()
    result = adapt_and_validate({"path": path, "adapter_type": adapter_type, "repo": repo}, adapters, provenance)
    if not result.accepted or not result.canonical:
        error_payload = {
            "file_path": path,
            "validation_errors": result.diagnostics,
            "adapter_type": result.adapter_type,
            "provenance": provenance.records[-1] if provenance.records else {},
        }
        logger.warning("Skill skipped due to adapter rejection", extra=error_payload)
        return {"error": error_payload}

    return {
        "name": result.canonical["name"],
        "version": result.canonical["version"],
        "description": result.canonical["description"],
        "path": path,
        "adapter_type": result.adapter_type,
        "provenance": provenance.records[-1],
    }


class HiClawClient:
    def nacos_register(self, service_name: str, metadata: dict, retries: int = 3, retry_delay: float = 0.5) -> bool:
        query_params = urllib.parse.urlencode({
            "serviceName": service_name,
            "ip": "127.0.0.1",
            "port": 8000,
            "ephemeral": "false",
        })
        url = f"http://hiclaw-manager:18789/nacos/v1/ns/instance?{query_params}"
        for attempt in range(1, retries + 1):
            try:
                response = httpx.post(url, json=metadata)
                response.raise_for_status()
                logger.info(f"Registered {service_name} with Nacos")
                return True
            except Exception as e:
                logger.warning(
                    "Nacos registration attempt failed",
                    extra={"service_name": service_name, "attempt": attempt, "retries": retries, "error": str(e)},
                )
                if attempt < retries:
                    time.sleep(retry_delay)

        logger.error(
            "Nacos dead-letter: exhausted retries",
            extra={"service_name": service_name, "metadata": metadata, "retries": retries},
        )
        return False


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
        self._skill_versions: dict[str, str] = {}

    @staticmethod
    def _is_skill_event(event) -> bool:
        return (not getattr(event, "is_directory", False)) and Path(event.src_path).name == "SKILL.md"

    def on_created(self, event):
        if self._is_skill_event(event):
            self._reload_skill(event.src_path, "ADDED")

    def on_modified(self, event):
        if self._is_skill_event(event):
            self._reload_skill(event.src_path, "UPDATED")

    def _reload_skill(self, path: str, action: str):
        metadata = parse_skill_metadata(path)
        if not metadata or metadata.get("error"):
            logger.warning("Skill skipped due to invalid metadata", extra={"skill_path": path, "action": action, "metadata": metadata})
            return

        skill_name = metadata["name"]
        version = metadata["version"]
        previous_version = self._skill_versions.get(skill_name)

        if previous_version == version:
            logger.info(
                "Skipping unchanged skill registration",
                extra={"skill_name": skill_name, "version": version, "path": path},
            )
            return

        effective_action = "UPDATED" if previous_version else "ADDED"

        registered = self.hiclaw.nacos_register(
            service_name=f"skill.{skill_name}",
            metadata={"version": version, "path": path, "action": effective_action},
        )

        if not registered:
            self.matrix.send_to_room(
                room="#skill-updates:daemon.local",
                message=f"❌ Skill FAILED: `{skill_name}` v{version} — registration failed after retries",
            )
            return

        self._skill_versions[skill_name] = version

        self.matrix.send_to_room(
            room="#skill-updates:daemon.local",
            message=f"🧠 Skill {effective_action}: `{skill_name}` v{version} — hot-reloaded",
        )


async def _main():
    event_handler = SkillHotReloader()
    observer = Observer()
    observer.schedule(event_handler, path="/var/lib/daemon/skills", recursive=True)
    observer.start()
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()

if __name__ == "__main__":
    import asyncio
    asyncio.run(_main())
