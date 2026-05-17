from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import httpx
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SkillRegistry")

# --- Mocks ---
def parse_skill_name(path): return path.split("/")[-1].replace(".md", "")
def parse_skill_version(path): return "1.0.0"
# -------------

class HiClawClient:
    def nacos_register(self, service_name: str, metadata: dict):
        url = "http://hiclaw-manager:18789/nacos/v1/ns/instance"
        payload = {
            "serviceName": service_name,
            "ip": "localhost",
            "port": 8000,
            "metadata": metadata
        }
        try:
            httpx.post(url, json=payload)
            logger.info(f"Registered {service_name} with Nacos")
        except Exception as e:
            logger.error(f"Failed to register with Nacos: {e}")

class MatrixClient:
    def send_to_room(self, room: str, message: str):
        # We replace `#` and `:` from the room ID for the URL placeholder, or pass it encoded
        # In a real Matrix implementation we'd encode the room_id correctly.
        room_id = room.replace("#", "%23").replace(":", "%3A")
        url = f"http://tuwunel-matrix:8008/_matrix/client/v3/rooms/{room_id}/send/m.room.message"
        payload = {
            "msgtype": "m.text",
            "body": message
        }
        try:
            httpx.post(url, json=payload)
            logger.info(f"Sent Matrix notification to {room}")
        except Exception as e:
            logger.error(f"Failed to send Matrix notification: {e}")

class SkillHotReloader(FileSystemEventHandler):
    def __init__(self):
        self.hiclaw = HiClawClient()
        self.matrix = MatrixClient()

    def on_created(self, event):
        if event.src_path.endswith(".md"): self._reload_skill(event.src_path, "ADDED")

    def on_modified(self, event):
        if event.src_path.endswith(".md"): self._reload_skill(event.src_path, "UPDATED")

    def _reload_skill(self, path: str, action: str):
        skill_name = parse_skill_name(path)
        version    = parse_skill_version(path)

        self.hiclaw.nacos_register(
            service_name=f"skill.{skill_name}",
            metadata={"version": version, "path": path, "action": action}
        )

        self.matrix.send_to_room(
            room="#skill-updates:daemon.local",
            message=f"🧠 Skill {action}: `{skill_name}` v{version} — hot-reloaded"
        )
