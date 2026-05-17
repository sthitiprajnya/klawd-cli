import schedule, time, httpx
import uuid
import logging
from sentence_transformers import SentenceTransformer, util

logger = logging.getLogger("CompetitiveCron")
model = SentenceTransformer("all-mpnet-base-v2")
ABSORPTION_THRESHOLD = 0.72

DAEMON_CAPABILITY_DESCRIPTION = "Autonomous AI engineering daemon with absorption pipeline, multi-agent orchestration, 5-layer memory hierarchy, LLM-based code generation, and security enforcement."
daemon_emb = model.encode(DAEMON_CAPABILITY_DESCRIPTION)

def fetch_trending_repos() -> list[dict]:
    # Real fetch to GitHub Search API for trending AI repos
    try:
        resp = httpx.get(
            "https://api.github.com/search/repositories?q=topic:ai+topic:llm&sort=stars&order=desc",
            headers={"User-Agent": "Klawd-CLI-Daemon"},
            timeout=10.0
        )
        return resp.json().get("items", [])[:10]
    except Exception as e:
        logger.error(f"Failed to fetch repos: {e}")
        return []

def compute_relevance(repo: dict) -> float:
    repo_text = f"{repo.get('name', '')} {repo.get('description', '')}"
    repo_emb = model.encode(repo_text)
    return float(util.cos_sim(daemon_emb, repo_emb))

def competitive_absorption_run():
    repos = fetch_trending_repos()

    # Query agentmemory for already absorbed targets
    try:
        mem_resp = httpx.post("http://agentmemory:3111", json={"jsonrpc": "2.0", "method": "memory_smart_search", "params": {"query": "absorbed repositories"}})
        already_absorbed = mem_resp.json().get("result", []) if mem_resp.status_code == 200 else []
    except Exception as e:
        logger.warning(f"Agent memory error: {e}")
        already_absorbed = []

    for repo in repos:
        url = repo["html_url"]
        relevance = compute_relevance(repo)

        if url not in str(already_absorbed) and relevance >= ABSORPTION_THRESHOLD:
            try:
                # Send payload directly to FastAPI job queue
                httpx.post("http://localhost:8000/api/v1/jobs", json={"task": f"absorb {url}"})

                # Notify Matrix
                txn_id = str(uuid.uuid4())
                httpx.put(
                    f"http://tuwunel-matrix:8008/_matrix/client/v3/rooms/%23daemon-ops%3Adaemon.local/send/m.room.message/{txn_id}",
                    json={"msgtype": "m.text", "body": f"🔍 Auto-queued: {url} (relevance={relevance:.2f})"}
                )
            except Exception as e:
                logger.error(f"Failed to queue or notify for {url}: {e}")

            time.sleep(1800) # 30 min gap to preserve rate limits

schedule.every().sunday.at("03:00").do(competitive_absorption_run)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(60)
