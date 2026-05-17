import os
import uuid
import httpx
import logging
import urllib.parse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SkillRegistry")

def parse_skill_name(path):
    return path.split("/")[-1].replace(".md", "")

def parse_skill_version(path):
    return "1.0.0"  # In production, parse from YAML frontmatter

class HiClawClient:
    def nacos_register(self, service_name: str, metadata: dict):
        # Nacos requires parameters in the query string, not just JSON body
        query_params = urllib.parse.urlencode({
            "serviceName": service_name,
            "ip": "127.0.0.1",
            "port": 8000,
            "ephemeral": "false"
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
        # Matrix requires URL-encoded room IDs and a unique transaction ID for PUT requests
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
        if event.src_path.endswith(".md"):
            self._reload_skill(event.src_path, "ADDED")

    def on_modified(self, event):
        if event.src_path.endswith(".md"):
            self._reload_skill(event.src_path, "UPDATED")

    def _reload_skill(self, path: str, action: str):
        skill_name = parse_skill_name(path)
        version = parse_skill_version(path)

        self.hiclaw.nacos_register(
            service_name=f"skill.{skill_name}",
            metadata={"version": version, "path": path, "action": action}
        )

        self.matrix.send_to_room(
            room="#skill-updates:daemon.local",
            message=f"🧠 Skill {action}: `{skill_name}` v{version} — hot-reloaded"
        )

if __name__ == "__main__":
    # Watchdog native event loop implementation
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
