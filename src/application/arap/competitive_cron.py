import schedule, time

# --- Mocks ---
class ARAPQueue:
    def enqueue(self, *args, **kwargs): pass
def notify_matrix(**kwargs): pass
class SentenceTransformerMock:
    def encode(self, txt): return [0.1, 0.2]
def cos_sim_mock(a, b): return 0.85
# -------------

model = SentenceTransformerMock()
ABSORPTION_THRESHOLD = 0.72

def fetch_trending_repos() -> list[dict]:
    # Mocking httpx call
    return [{"name": "repo1", "description": "ai tool", "html_url": "github.com/org/repo1"}]

def compute_relevance(repo: dict) -> float:
    return cos_sim_mock(model.encode("daemon capability"), model.encode(repo.get("description", "")))

def competitive_absorption_run():
    repos = fetch_trending_repos()
    already_absorbed = [] # mempalace.list_hall(...) mock

    for repo in repos:
        url = repo["html_url"]
        relevance = compute_relevance(repo)
        if url not in already_absorbed and relevance >= ABSORPTION_THRESHOLD:
            ARAPQueue().enqueue(url, priority="low", source="competitive-cron")
            notify_matrix(room="#daemon-ops:daemon.local", message=f"🔍 Queued: {url}")

schedule.every().sunday.at("03:00").do(competitive_absorption_run)

if __name__ == "__main__":
    pass # To allow module to load successfully without blocking in test/CI
    # while True:
    #     schedule.run_pending()
    #     time.sleep(60)