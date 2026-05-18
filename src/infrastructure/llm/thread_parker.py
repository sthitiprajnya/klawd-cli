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

def get_all_configured_keys(pool: str) -> list[str]:
    # pool kept for forward compatibility with pool-specific key namespaces.
    _ = pool
    return [os.getenv(f"NIM_API_KEY_{i}") for i in range(1, 6) if os.getenv(f"NIM_API_KEY_{i}")]

def hiclaw_notify(msg: str):
    try:
        txn_id = str(uuid.uuid4())
        url = f"http://tuwunel-matrix:8008/_matrix/client/v3/rooms/%23daemon-ops%3Adaemon.local/send/m.room.message/{txn_id}"
        response = httpx.put(url, json={"msgtype": "m.text", "body": f"⚠️ {msg}"}, timeout=10.0)
        if response.status_code >= 400:
            logger.error(f"Matrix notification failed: status={response.status_code} body={response.text}")
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
        configured_keys = get_all_configured_keys(model_pool)
        if not configured_keys:
            logger.warning(f"No API keys configured for pool={model_pool}")
            return None

        for key in configured_keys:
            cooldown_key = f"litellm:cooldown:{model_pool}:{key}"
            if not r.exists(cooldown_key):
                return key
        return None
