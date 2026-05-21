import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ExternalSkillRepo:
    repo_url: str
    pinned_ref: str
    enabled: bool = True
    subdir: str | None = None


class Settings:
    dedup_similarity_threshold: float = float(os.getenv("DEDUP_SIMILARITY_THRESHOLD", "0.8"))
    mempalace_base_url: str = os.getenv("MEMPALACE_BASE_URL", "http://mempalace:8000")
    mempalace_semantic_top_k: int = int(os.getenv("MEMPALACE_SEMANTIC_TOP_K", "5"))
    mempalace_semantic_max_chars: int = int(os.getenv("MEMPALACE_SEMANTIC_MAX_CHARS", "2000"))
    external_skill_repos: list[ExternalSkillRepo] = [
        ExternalSkillRepo(
            repo_url="https://github.com/CyberStrikeus/CyberStrike",
            pinned_ref="0000000000000000000000000000000000000000",
            enabled=False,
        ),
        ExternalSkillRepo(
            repo_url="https://github.com/0x4m4/hexstrike-ai",
            pinned_ref="0000000000000000000000000000000000000000",
            enabled=False,
        ),
    ]


settings = Settings()
