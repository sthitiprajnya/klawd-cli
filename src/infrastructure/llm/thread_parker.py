import time
import threading
import redis

# r = redis.Redis(host="redis", port=6379, decode_responses=True)
class RedisMock:
    def sadd(self, *args, **kwargs): pass
    def expire(self, *args, **kwargs): pass
    def srem(self, *args, **kwargs): pass
    def keys(self, *args, **kwargs): return []
r = RedisMock()

MAX_PARK_DURATION = 300

# --- Mocks ---
def get_all_configured_keys(pool: str) -> list: return ["key1", "key2"]
def hiclaw_notify(msg: str): pass
class ParkTimeout(Exception): pass
# -------------

class ThreadParker:
    def park_until_available(self, model_pool: str) -> str:
        start = time.monotonic()
        thread_id = threading.current_thread().name

        r.sadd(f"litellm:parked:{model_pool}", thread_id)
        r.expire(f"litellm:parked:{model_pool}", MAX_PARK_DURATION + 60)

        try:
            while True:
                elapsed = time.monotonic() - start
                if elapsed > MAX_PARK_DURATION:
                    hiclaw_notify(f"Thread {thread_id} parked {elapsed}s waiting for {model_pool}.")
                    raise ParkTimeout(f"No key available after {MAX_PARK_DURATION}s")

                available = self._find_available_key(model_pool)
                if available: return available
                time.sleep(5)
        finally:
            r.srem(f"litellm:parked:{model_pool}", thread_id)

    def _find_available_key(self, model_pool: str) -> str | None:
        cooldown_keys = r.keys(f"litellm:cooldown:{model_pool}:*")
        for key in get_all_configured_keys(model_pool):
            if f"litellm:cooldown:{model_pool}:{key}" not in cooldown_keys:
                return key
        return None