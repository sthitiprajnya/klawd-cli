import logging
import re
import shutil
import subprocess
from pathlib import Path

from src.settings import EXTERNAL_SKILL_SOURCES, ExternalSkillSource

logger = logging.getLogger("ExternalSkillIngestion")

PINNED_SHA_PATTERN = re.compile(r"^[0-9a-f]{7,40}$")


class ExternalSkillIngestionError(Exception):
    pass


def _validate_pinned_ref(source: ExternalSkillSource) -> None:
    if not PINNED_SHA_PATTERN.match(source.pinned_ref):
        raise ExternalSkillIngestionError(
            f"Source '{source.name}' must use a pinned commit SHA, got '{source.pinned_ref}'"
        )


def ingest_external_skill_sources(vendor_root: str = "src/infrastructure/skills/vendor") -> list[Path]:
    vendor_dir = Path(vendor_root)
    vendor_dir.mkdir(parents=True, exist_ok=True)

    materialized_paths: list[Path] = []
    for source in EXTERNAL_SKILL_SOURCES:
        if not source.enabled:
            continue

        _validate_pinned_ref(source)

        destination = vendor_dir / f"{source.name}@{source.pinned_ref[:12]}"
        if destination.exists():
            materialized_paths.append(destination)
            continue

        temp_dir = vendor_dir / f".{source.name}.tmp"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

        subprocess.run(
            ["git", "clone", "--depth", "1", source.repo_url, str(temp_dir)],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["git", "-C", str(temp_dir), "fetch", "--depth", "1", "origin", source.pinned_ref],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["git", "-C", str(temp_dir), "checkout", source.pinned_ref],
            check=True,
            capture_output=True,
            text=True,
        )

        temp_dir.rename(destination)
        logger.info("Ingested external skill source", extra={"source": source.name, "path": str(destination)})
        materialized_paths.append(destination)

    return materialized_paths
