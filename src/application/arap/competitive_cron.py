import schedule, time
import httpx
import logging
from openai import OpenAI
import numpy as np

logger = logging.getLogger("CompetitiveCron")

ABSORPTION_THRESHOLD = 0.72

llm_client = OpenAI(
    api_key="dummy-key",
    base_url="http://litellm-proxy:4000/v1"
)

def get_embedding(text: str) -> list[float]:
    try:
        response = llm_client.embeddings.create(
            model="text-embedding-3-small",
            input=[text]
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        return [0.0] * 1536

def cos_sim(a: list[float], b: list[float]) -> float:
    if sum(a) == 0 or sum(b) == 0: return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def notify_matrix(room: str, message: str):
    room_id = room.replace("#", "%23").replace(":", "%3A")
    url = f"http://tuwunel-matrix:8008/_matrix/client/v3/rooms/{room_id}/send/m.room.message"
    try:
        httpx.post(url, json={"msgtype": "m.text", "body": message})
    except Exception as e:
        logger.error(f"Failed to notify matrix: {e}")

def fetch_trending_repos() -> list[dict]:
    # Mocking httpx call for now
    return [{"name": "repo1", "description": "ai tool", "html_url": "github.com/org/repo1"}]

def compute_relevance(repo: dict) -> float:
    return cos_sim(get_embedding("daemon capability"), get_embedding(repo.get("description", "")))

def get_already_absorbed_repos() -> list[str]:
    try:
        response = httpx.get("http://mempalace:8000/api/v1/drawers/absorbed-knowledge/meta/dependency-graph")
        if response.status_code == 200:
            entries = response.json().get("entries", [])
            return [entry.get("content", {}).get("child") for entry in entries if "child" in entry.get("content", {})]
    except Exception as e:
        logger.warning(f"Failed to fetch already absorbed repos: {e}")
    return []

def competitive_absorption_run():
    repos = fetch_trending_repos()
    already_absorbed = get_already_absorbed_repos()

    for repo in repos:
        url = repo["html_url"]
        relevance = compute_relevance(repo)
        if url not in already_absorbed and relevance >= ABSORPTION_THRESHOLD:
            try:
                httpx.post("http://localhost:8000/api/v1/jobs", json={"task": f"Absorb: {url}"})
                notify_matrix(room="#daemon-ops:daemon.local", message=f"🔍 Queued: {url}")
            except Exception as e:
                logger.error(f"Failed to queue absorption job: {e}")

schedule.every().sunday.at("03:00").do(competitive_absorption_run)

if __name__ == "__main__":
    pass # To allow module to load successfully without blocking in test/CI
    # while True:
    #     schedule.run_pending()
    #     time.sleep(60)