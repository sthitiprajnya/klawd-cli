import logging
import os
from pathlib import Path

from src.domain.arap.skill_parser import parse_skill_frontmatter, validate_skill_schema
from src.infrastructure.registry.external_skill_ingestion import ExternalSkillIngestionError, ingest_external_skill_sources

logger = logging.getLogger("SkillManager")


class SkillManager:
    def __init__(self, skills_dir: str = "src/infrastructure/skills"):
        self.skills_dir = skills_dir
        self.loaded_skills: dict[str, dict] = {}
        os.makedirs(self.skills_dir, exist_ok=True)

    def list_skills(self) -> dict[str, dict]:
        return self.loaded_skills

    def discover_skill_files(self) -> list[Path]:
        return sorted(Path(self.skills_dir).rglob("SKILL.md"))

    def refresh_skills(self, include_external: bool = True) -> None:
        if include_external:
            from src.application.ingestion.service import ingest_external_skills_into_manager

            ingest_external_skills_into_manager(self)

        discovered: dict[str, dict] = {}
        try:
            ingest_external_skill_sources()
        except ExternalSkillIngestionError as exc:
            logger.warning("External skill ingestion skipped", extra={"error": str(exc)})
        except Exception as exc:
            logger.error("External skill ingestion failed", extra={"error": str(exc)})
        for skill_file in self.discover_skill_files():
            metadata = self.load_skill(skill_file)
            if metadata:
                discovered[metadata["name"]] = metadata
        self.loaded_skills = discovered

    def load_skill(self, skill_path: str | Path) -> dict | None:
        skill_path = Path(skill_path)
        try:
            content = skill_path.read_text(encoding="utf-8")
            frontmatter = parse_skill_frontmatter(content)
            is_valid, errors = validate_skill_schema(frontmatter)
            if not is_valid:
                logger.error(
                    "Invalid SKILL.md schema",
                    extra={
                        "skill_path": str(skill_path),
                        "errors": errors,
                    },
                )
                return None

            metadata = {
                "name": frontmatter["name"],
                "description": frontmatter["description"],
                "triggers": frontmatter["triggers"],
                "dependencies": frontmatter["dependencies"],
                "version": frontmatter["version"],
                "author": frontmatter["author"],
                "license": frontmatter["license"],
                "path": str(skill_path),
            }
            return metadata
        except Exception as exc:
            logger.error(
                "Failed to parse SKILL.md",
                extra={"skill_path": str(skill_path), "error": str(exc)},
            )
            return None


skill_manager = SkillManager()
skill_manager.refresh_skills()
