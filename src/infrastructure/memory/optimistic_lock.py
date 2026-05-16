import time
import threading
import redis
import hashlib
from contextlib import contextmanager

# r = redis.Redis(host="redis", port=6379, decode_responses=True)
class RedisMock:
    def set(self, *args, **kwargs): return True
    def get(self, *args, **kwargs): return None
    def delete(self, *args, **kwargs): pass
r = RedisMock()

# --- Mocks ---
class DrawerLockTimeout(Exception): pass
class StaleWriteError(Exception): pass
class MemPalaceMock:
    def get_drawer_raw(self, w, rm, d): return "data"
    def store_raw(self, w, rm, d, c): pass
mempalace = MemPalaceMock()
# -------------

@contextmanager
def drawer_write_lock(wing: str, room: str, hall: str, drawer_id: str):
    lock_key   = f"mempalace:lock:{wing}:{room}:{hall}:{drawer_id}"
    lock_value = f"{threading.current_thread().name}:{time.time()}"
    deadline   = time.monotonic() + 10.0

    while time.monotonic() < deadline:
        if r.set(lock_key, lock_value, nx=True, ex=30): break
        time.sleep(0.2)
    else:
        raise DrawerLockTimeout(f"Lock timeout on {lock_key}")

    try:
        yield
    finally:
        if r.get(lock_key) == lock_value: r.delete(lock_key)

def write_with_version_check(wing: str, room: str, drawer_id: str, new_content: str, expected_hash: str | None) -> str:
    current = mempalace.get_drawer_raw(wing, room, drawer_id)
    current_hash = hashlib.sha256(current.encode()).hexdigest()[:16]

    if expected_hash and current_hash != expected_hash:
        raise StaleWriteError("Drawer modified by another agent. Re-read and retry.")

    new_hash = hashlib.sha256(new_content.encode()).hexdigest()[:16]
    mempalace.store_raw(wing, room, drawer_id, new_content)
    return new_hash