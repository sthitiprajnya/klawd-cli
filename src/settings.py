import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ExternalSkillRepo:
    repo_url: str
    pinned_ref: str
    enabled: bool = True
    subdir: str | None = None
@dataclass(frozen=True)
class ExternalSkillSource:
    name: str
    repo_url: str
    pinned_ref: str
    enabled: bool = True


def _external_source(name: str, url: str, ref_env: str, default_ref: str) -> ExternalSkillSource:
    return ExternalSkillSource(
        name=name,
        repo_url=url,
        pinned_ref=os.getenv(ref_env, default_ref),
        enabled=os.getenv(f"{name.upper()}_ENABLED", "true").lower() == "true",
    )


EXTERNAL_SKILL_SOURCES: list[ExternalSkillSource] = [
    _external_source(
        "cyberstrike",
        "https://github.com/CyberStrikeus/CyberStrike",
        "CYBERSTRIKE_PINNED_REF",
        "main",
    ),
    _external_source(
        "hexstrike_ai",
        "https://github.com/0x4m4/hexstrike-ai",
        "HEXSTRIKE_AI_PINNED_REF",
        "main",
    ),
]


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
