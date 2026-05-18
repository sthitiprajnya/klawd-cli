import os
import time
import threading
import redis
import httpx
import uuid
import logging

logger = logging.getLogger("ThreadParker")
r = redis.Redis(host="redis", port=6379, decode_responses=True)

MAX_PARK_DURATION = 300

def get_all_configured_keys(pool: str) -> list:
    keys = [os.getenv(f"NIM_API_KEY_{i}") for i in range(1, 6) if os.getenv(f"NIM_API_KEY_{i}")]
    return keys if keys else ["dummy-key"]

def hiclaw_notify(msg: str):
    try:
        url = f"http://tuwunel-matrix:8008/_matrix/client/v3/rooms/%23daemon-ops%3Adaemon.local/send/m.room.message/{uuid.uuid4()}"
        httpx.put(url, json={"msgtype": "m.text", "body": f"⚠️ {msg}"})
    except Exception as e:
        logger.error(f"Failed to send Matrix notification: {e}")

class ParkTimeout(Exception): pass

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
                    msg = f"Thread {thread_id} parked {elapsed:.1f}s waiting for {model_pool}."
                    logger.error(msg)
                    hiclaw_notify(msg)
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
