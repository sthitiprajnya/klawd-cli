import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.domain.arap.skill_parser import parse_skill_frontmatter, validate_skill_schema

logger = logging.getLogger("SkillAdapters")


@dataclass
class AdapterResult:
    accepted: bool
    canonical: dict[str, Any] | None
    diagnostics: list[str]
    adapter_type: str


class SkillMetadataAdapter(ABC):
    adapter_type: str = "native"

    @abstractmethod
    def normalize(self, repo_entry: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class NativeSkillMdAdapter(SkillMetadataAdapter):
    adapter_type = "native"

    def normalize(self, repo_entry: dict[str, Any]) -> dict[str, Any]:
        source_path = Path(repo_entry["path"])
        content = source_path.read_text(encoding="utf-8")
        return parse_skill_frontmatter(content)


class RepoSkillJsonAdapter(SkillMetadataAdapter):
    """Adapter for repos that expose metadata in a skill.json contract."""

    adapter_type = "repo_skill_json"

    def normalize(self, repo_entry: dict[str, Any]) -> dict[str, Any]:
        source_path = Path(repo_entry["path"])
        payload = json.loads(source_path.read_text(encoding="utf-8"))
        return {
            "name": payload.get("skill_name", ""),
            "description": payload.get("summary", ""),
            "triggers": payload.get("activation", []),
            "dependencies": payload.get("requires", []),
            "version": payload.get("semver", ""),
            "author": payload.get("owner", ""),
            "license": payload.get("license", ""),
        }


class RepoManifestYamlAdapter(SkillMetadataAdapter):
    """Adapter for repos that publish metadata under a manifest envelope."""

    adapter_type = "repo_manifest_yaml"

    def normalize(self, repo_entry: dict[str, Any]) -> dict[str, Any]:
        source_path = Path(repo_entry["path"])
        frontmatter = parse_skill_frontmatter(source_path.read_text(encoding="utf-8"))
        meta = frontmatter.get("manifest", {})
        return {
            "name": meta.get("id", ""),
            "description": meta.get("about", ""),
            "triggers": meta.get("triggers", []),
            "dependencies": meta.get("dependencies", []),
            "version": meta.get("version", ""),
            "author": meta.get("author", ""),
            "license": meta.get("license", ""),
        }


class SkillAdapterRegistry:
    def __init__(self):
        self._adapters: dict[str, SkillMetadataAdapter] = {
            NativeSkillMdAdapter.adapter_type: NativeSkillMdAdapter(),
            RepoSkillJsonAdapter.adapter_type: RepoSkillJsonAdapter(),
            RepoManifestYamlAdapter.adapter_type: RepoManifestYamlAdapter(),
        }

    def get(self, adapter_type: str | None) -> SkillMetadataAdapter:
        return self._adapters.get(adapter_type or "native", self._adapters["native"])


class SkillProvenanceManifest:
    def __init__(self):
        self.records: list[dict[str, Any]] = []

    def record(self, *, repo: str, source_path: str, adapter_type: str, accepted: bool, diagnostics: list[str]):
        self.records.append(
            {
                "repo": repo,
                "source_path": source_path,
                "adapter_type": adapter_type,
                "accepted": accepted,
                "diagnostics": diagnostics,
            }
        )


def adapt_and_validate(repo_entry: dict[str, Any], adapters: SkillAdapterRegistry, manifest: SkillProvenanceManifest) -> AdapterResult:
    repo_name = repo_entry.get("repo", "unknown")
    adapter = adapters.get(repo_entry.get("adapter_type"))
    diagnostics: list[str] = []
    canonical: dict[str, Any] | None = None

    try:
        canonical = adapter.normalize(repo_entry)
        is_valid, errors = validate_skill_schema(canonical)
        if not is_valid:
            diagnostics = errors
            logger.error("Rejected skill repo after normalization", extra={"repo": repo_name, "adapter_type": adapter.adapter_type, "errors": errors})
            manifest.record(repo=repo_name, source_path=repo_entry["path"], adapter_type=adapter.adapter_type, accepted=False, diagnostics=diagnostics)
            return AdapterResult(False, None, diagnostics, adapter.adapter_type)

        manifest.record(repo=repo_name, source_path=repo_entry["path"], adapter_type=adapter.adapter_type, accepted=True, diagnostics=[])
        return AdapterResult(True, canonical, [], adapter.adapter_type)
    except Exception as exc:
        diagnostics = [f"adapter failure: {exc}"]
        logger.error("Adapter execution failed", extra={"repo": repo_name, "adapter_type": adapter.adapter_type, "diagnostics": diagnostics})
        manifest.record(repo=repo_name, source_path=repo_entry["path"], adapter_type=adapter.adapter_type, accepted=False, diagnostics=diagnostics)
        return AdapterResult(False, None, diagnostics, adapter.adapter_type)
