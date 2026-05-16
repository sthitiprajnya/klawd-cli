from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- Mocks ---
def parse_skill_name(path): return path.split("/")[-1].replace(".md", "")
def parse_skill_version(path): return "1.0.0"
class HiClawMock:
    def nacos_register(self, **kwargs): pass
class MatrixMock:
    def send_to_room(self, **kwargs): pass
# -------------

class SkillHotReloader(FileSystemEventHandler):
    def __init__(self):
        self.hiclaw = HiClawMock()
        self.matrix = MatrixMock()

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