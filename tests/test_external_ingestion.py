from pathlib import Path

from src.application.ingestion.service import ExternalSkillIngestionService
from src.domain.skills import SkillManager
from src.infrastructure.ingestion.repo_ingestor import ExternalRepoIngestor, SkillIngestionError
from src.settings import ExternalSkillRepo


def _skill_md(name: str = "vendor-skill") -> str:
    return f"""---
name: {name}
description: Ingested skill
triggers:
  - ingest
dependencies:
  - requests
version: 1.0.0
author: vendor
license: MIT
---
# Skill
"""


def _write_repo(workspace: Path, repo_name: str, content: str) -> Path:
    repo_dir = workspace / repo_name
    repo_dir.mkdir(parents=True)
    (repo_dir / "SKILL.md").write_text(content, encoding="utf-8")
    return repo_dir


def test_successful_ingest_and_discover(monkeypatch, tmp_path: Path):
    ingestor = ExternalRepoIngestor(vendor_root=str(tmp_path / "vendor"), production_mode=True)
    source_repo = _write_repo(tmp_path, "source", _skill_md())

    def _run_git(args, repo):
        if args[0] == "clone":
            target = Path(args[-1])
            target.mkdir(parents=True, exist_ok=True)
            (target / "SKILL.md").write_text((source_repo / "SKILL.md").read_text(encoding="utf-8"), encoding="utf-8")

    monkeypatch.setattr(ingestor, "_run_git", _run_git)

    repo_cfg = ExternalSkillRepo(repo_url="https://github.com/example/source", pinned_ref="a" * 40, enabled=True)
    ingested = ingestor.ingest(repo_cfg)
    assert ingested[0].name == "vendor-skill"

    manager = SkillManager(skills_dir=str(tmp_path / "vendor"))
    manager.refresh_skills(include_external=False)
    assert "vendor-skill" in manager.list_skills()


def test_missing_skill_md(monkeypatch, tmp_path: Path):
    ingestor = ExternalRepoIngestor(vendor_root=str(tmp_path / "vendor"), production_mode=True)

    def _run_git(args, repo):
        if args[0] == "clone":
            Path(args[-1]).mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(ingestor, "_run_git", _run_git)
    repo_cfg = ExternalSkillRepo(repo_url="https://github.com/example/empty", pinned_ref="b" * 40, enabled=True)

    try:
        ingestor.ingest(repo_cfg)
        assert False, "expected SkillIngestionError"
    except SkillIngestionError as exc:
        assert exc.code == "MISSING_SKILL_MD"


def test_invalid_frontmatter(monkeypatch, tmp_path: Path):
    ingestor = ExternalRepoIngestor(vendor_root=str(tmp_path / "vendor"), production_mode=True)

    def _run_git(args, repo):
        if args[0] == "clone":
            target = Path(args[-1])
            target.mkdir(parents=True, exist_ok=True)
            (target / "SKILL.md").write_text("---\nname: bad\n---\n", encoding="utf-8")

    monkeypatch.setattr(ingestor, "_run_git", _run_git)
    repo_cfg = ExternalSkillRepo(repo_url="https://github.com/example/bad", pinned_ref="c" * 40, enabled=True)

    try:
        ingestor.ingest(repo_cfg)
        assert False, "expected SkillIngestionError"
    except SkillIngestionError as exc:
        assert exc.code == "INVALID_SKILL_METADATA"


def test_reject_non_pinned_ref():
    ingestor = ExternalRepoIngestor(production_mode=True)
    repo_cfg = ExternalSkillRepo(repo_url="https://github.com/example/floating", pinned_ref="main", enabled=True)

    try:
        ingestor.ingest(repo_cfg)
        assert False, "expected SkillIngestionError"
    except SkillIngestionError as exc:
        assert exc.code == "NON_PINNED_REF"


def test_service_emits_structured_errors(monkeypatch):
    service = ExternalSkillIngestionService(ingestor=ExternalRepoIngestor(production_mode=True))

    def _ingest(_repo):
        raise SkillIngestionError("INVALID_SKILL_METADATA", "bad", {"skill_path": "x"})

    monkeypatch.setattr(service.ingestor, "ingest", _ingest)
    results = service.ingest_all([
        ExternalSkillRepo(repo_url="https://github.com/example/x", pinned_ref="d" * 40, enabled=True)
    ])

    assert results == [
        {"repo_url": "https://github.com/example/x", "status": "error", "error_code": "INVALID_SKILL_METADATA"}
    ]
