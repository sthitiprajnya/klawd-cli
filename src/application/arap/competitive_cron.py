import schedule, time, httpx
import asyncio
import uuid
import logging
import datetime
from sentence_transformers import SentenceTransformer, util
from src.infrastructure.database import SessionLocal
from src.infrastructure.provenance import ProvenanceRecord, repo_provenance_store

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

async def _queue_and_notify_async(client: httpx.AsyncClient, url: str, relevance: float):
    try:
        # Send payload directly to FastAPI job queue
        await client.post("http://localhost:8000/api/v1/jobs", json={"task": f"absorb {url}"})

        # Notify Matrix
        txn_id = str(uuid.uuid4())
        await client.put(
            f"http://tuwunel-matrix:8008/_matrix/client/v3/rooms/%23daemon-ops%3Adaemon.local/send/m.room.message/{txn_id}",
            json={"msgtype": "m.text", "body": f"🔍 Auto-queued: {url} (relevance={relevance:.2f})"}
        )
    except Exception as e:
        logger.error(f"Failed to queue or notify for {url}: {e}")

def competitive_absorption_run():
    repos = fetch_trending_repos()

    # Query agentmemory for already absorbed targets
    try:
        mem_resp = httpx.post("http://agentmemory:3111", json={"jsonrpc": "2.0", "method": "memory_smart_search", "params": {"query": "absorbed repositories"}})
        already_absorbed = mem_resp.json().get("result", []) if mem_resp.status_code == 200 else []
    except Exception as e:
        logger.warning(f"Agent memory error: {e}")
        already_absorbed = []

    tasks_to_run = []

    for repo in repos:
        url = repo["html_url"]
        relevance = compute_relevance(repo)
        pinned_sha = repo.get("default_branch", "unknown")
        policy_decision = "allow" if relevance >= ABSORPTION_THRESHOLD else "deny"
        policy_reason = "meets_relevance_threshold" if policy_decision == "allow" else "below_relevance_threshold"

        db = SessionLocal()
        try:
            repo_provenance_store.write_record_atomic(
                db,
                ProvenanceRecord(
                    repo_url=url,
                    pinned_sha=pinned_sha,
                    ingest_timestamp=datetime.datetime.utcnow(),
                    discovered_skills=[],
                    validation_status="pending_discovery",
                    policy_decision=policy_decision,
                    policy_reason=policy_reason,
                ),
            )
        finally:
            db.close()

        if url not in str(already_absorbed) and policy_decision == "allow":
            # Pass lambda or closure to defer creation until _run_all
            tasks_to_run.append((url, relevance))

    async def _run_all():
        async with httpx.AsyncClient() as client:
            for i, (u, r) in enumerate(tasks_to_run):
                await _queue_and_notify_async(client, u, r)
                # Add delay to preserve rate limits per the original design, but unblocked.
                # Only sleep if it is not the last item.
                if i < len(tasks_to_run) - 1:
                    await asyncio.sleep(1800)

    if tasks_to_run:
        # We fire the background queue processing as a detached async task
        # so it doesn't block the main schedule loop thread.
        # Since schedule blocks the main thread, we spawn a thread to run the async loop
        import threading
        def _run_in_thread():
            asyncio.run(_run_all())
        threading.Thread(target=_run_in_thread, daemon=True).start()

schedule.every().sunday.at("03:00").do(competitive_absorption_run)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(60)
