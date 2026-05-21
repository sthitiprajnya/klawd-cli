import logging
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from src.domain.arap.skill_parser import parse_skill_frontmatter, validate_skill_schema
from src.settings import ExternalSkillRepo

logger = logging.getLogger("SkillIngestor")
HEX40_RE = re.compile(r"^[0-9a-f]{40}$", re.IGNORECASE)
IMMUTABLE_TAG_RE = re.compile(r"^v?\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")


class SkillIngestionError(Exception):
    def __init__(self, code: str, message: str, context: dict | None = None):
        super().__init__(message)
        self.code = code
        self.context = context or {}


@dataclass(frozen=True)
class IngestedSkill:
    name: str
    path: str
    source_repo: str
    source_ref: str


def _repo_name(repo_url: str) -> str:
    return repo_url.rstrip("/").split("/")[-1]


def _is_pinned_ref(ref: str) -> bool:
    return bool(HEX40_RE.match(ref) or IMMUTABLE_TAG_RE.match(ref))


class ExternalRepoIngestor:
    def __init__(self, vendor_root: str = "src/infrastructure/skills/vendor", production_mode: bool = True):
        self.vendor_root = Path(vendor_root)
        self.vendor_root.mkdir(parents=True, exist_ok=True)
        self.production_mode = production_mode

    def ingest(self, repo: ExternalSkillRepo) -> list[IngestedSkill]:
        if self.production_mode and not _is_pinned_ref(repo.pinned_ref):
            raise SkillIngestionError(
                code="NON_PINNED_REF",
                message="External repository ref must be immutable in production mode",
                context={"repo_url": repo.repo_url, "pinned_ref": repo.pinned_ref},
            )

        target = self.vendor_root / f"{_repo_name(repo.repo_url)}@{repo.pinned_ref[:12]}"
        if target.exists():
            shutil.rmtree(target)

        self._run_git(["clone", "--no-checkout", repo.repo_url, str(target)], repo)
        self._run_git(["-C", str(target), "checkout", repo.pinned_ref], repo)

        scan_root = target / repo.subdir if repo.subdir else target
        skill_files = sorted(scan_root.rglob("SKILL.md")) if scan_root.exists() else []
        if not skill_files:
            raise SkillIngestionError(
                code="MISSING_SKILL_MD",
                message="No SKILL.md found for ingested repository",
                context={"repo_url": repo.repo_url, "scan_root": str(scan_root)},
            )

        ingested: list[IngestedSkill] = []
        for skill_file in skill_files:
            parsed = self._validate_skill_file(skill_file)
            ingested.append(
                IngestedSkill(
                    name=parsed["name"],
                    path=str(skill_file),
                    source_repo=repo.repo_url,
                    source_ref=repo.pinned_ref,
                )
            )
        return ingested

    def _validate_skill_file(self, skill_file: Path) -> dict:
        content = skill_file.read_text(encoding="utf-8")
        frontmatter = parse_skill_frontmatter(content)
        is_valid, errors = validate_skill_schema(frontmatter)
        if not is_valid:
            raise SkillIngestionError(
                code="INVALID_SKILL_METADATA",
                message="Invalid SKILL.md schema",
                context={"skill_path": str(skill_file), "validation_errors": errors},
            )
        return frontmatter

    def _run_git(self, args: list[str], repo: ExternalSkillRepo) -> None:
        result = subprocess.run(["git", *args], capture_output=True, text=True)
        if result.returncode != 0:
            raise SkillIngestionError(
                code="GIT_FAILURE",
                message="Git operation failed during skill ingestion",
                context={
                    "repo_url": repo.repo_url,
                    "args": args,
                    "stderr": result.stderr.strip(),
                },
            )
