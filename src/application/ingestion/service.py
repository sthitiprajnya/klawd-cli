import logging

from src.domain.skills import SkillManager
from src.infrastructure.ingestion.repo_ingestor import ExternalRepoIngestor, SkillIngestionError
from src.settings import ExternalSkillRepo, settings

logger = logging.getLogger("ExternalSkillIngestionService")


class ExternalSkillIngestionService:
    def __init__(self, ingestor: ExternalRepoIngestor | None = None):
        self.ingestor = ingestor or ExternalRepoIngestor()

    def ingest_all(self, repos: list[ExternalSkillRepo] | None = None) -> list[dict]:
        repos = repos or settings.external_skill_repos
        results: list[dict] = []
        for repo in repos:
            if not repo.enabled:
                continue
            try:
                skills = self.ingestor.ingest(repo)
                results.append({"repo_url": repo.repo_url, "status": "ok", "skills": [s.name for s in skills]})
            except SkillIngestionError as exc:
                logger.error(
                    "External skill ingestion failed",
                    extra={"error_code": exc.code, **exc.context},
                )
                results.append({"repo_url": repo.repo_url, "status": "error", "error_code": exc.code})
        return results


def ingest_external_skills_into_manager(skill_manager: SkillManager) -> list[dict]:
    _ = skill_manager
    service = ExternalSkillIngestionService()
    return service.ingest_all()
