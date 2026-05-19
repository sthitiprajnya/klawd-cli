import os


class Settings:
    dedup_similarity_threshold: float = float(os.getenv("DEDUP_SIMILARITY_THRESHOLD", "0.8"))
    mempalace_base_url: str = os.getenv("MEMPALACE_BASE_URL", "http://mempalace:8000")
    mempalace_semantic_top_k: int = int(os.getenv("MEMPALACE_SEMANTIC_TOP_K", "5"))
    mempalace_semantic_max_chars: int = int(os.getenv("MEMPALACE_SEMANTIC_MAX_CHARS", "2000"))


settings = Settings()
