from pathlib import Path
from types import SimpleNamespace

from src.domain.arap.skill_parser import parse_skill_frontmatter, validate_skill_schema
from src.domain.skills import SkillManager
from src.infrastructure.registry.skill_registry import parse_skill_metadata
from src.infrastructure.registry.skill_registry import HiClawClient, SkillHotReloader
from src.infrastructure.registry.skill_adapters import SkillAdapterRegistry, SkillProvenanceManifest, adapt_and_validate


def _valid_skill_md() -> str:
    return """---
name: test-skill
description: A test skill
triggers:
  - test
dependencies:
  - requests
version: 1.0.0
author: test-author
license: MIT
---
# Test Skill
"""


def _missing_fields_skill_md() -> str:
    return """---
name: bad-skill
version: 1.0.0
---
# Bad Skill
"""


def _wrong_type_skill_md() -> str:
    return """---
name: test-skill
description: A test skill
triggers: test
dependencies:
  - requests
version: 1.0.0
author: test-author
license: MIT
---
# Test Skill
"""


def _empty_list_skill_md() -> str:
    return """---
name: test-skill
description: A test skill
triggers: []
dependencies: []
version: 1.0.0
author: test-author
license: MIT
---
# Test Skill
"""


def test_parse_valid_skill_schema():
    frontmatter = parse_skill_frontmatter(_valid_skill_md())
    is_valid, errors = validate_skill_schema(frontmatter)

    assert is_valid is True
    assert errors == []


def test_reject_missing_required_fields():
    frontmatter = parse_skill_frontmatter(_missing_fields_skill_md())
    is_valid, errors = validate_skill_schema(frontmatter)

    assert is_valid is False
    assert "missing required field 'description'" in errors
    assert "missing required field 'triggers'" in errors


def test_reject_wrong_type_fields():
    frontmatter = parse_skill_frontmatter(_wrong_type_skill_md())
    is_valid, errors = validate_skill_schema(frontmatter)

    assert is_valid is False
    assert "field 'triggers' must be of type list, got str" in errors


def test_reject_empty_list_fields():
    frontmatter = parse_skill_frontmatter(_empty_list_skill_md())
    is_valid, errors = validate_skill_schema(frontmatter)

    assert is_valid is False
    assert "field 'triggers' must not be empty" in errors
    assert "field 'dependencies' must not be empty" in errors


def test_registry_and_manager_skip_invalid_skill_files(tmp_path: Path):
    valid_dir = tmp_path / "valid"
    valid_dir.mkdir()
    valid_skill = valid_dir / "SKILL.md"
    valid_skill.write_text(_valid_skill_md(), encoding="utf-8")

    invalid_dir = tmp_path / "invalid"
    invalid_dir.mkdir()
    invalid_skill = invalid_dir / "SKILL.md"
    invalid_skill.write_text(_missing_fields_skill_md(), encoding="utf-8")

    non_skill = tmp_path / "README.md"
    non_skill.write_text("not a skill", encoding="utf-8")

    assert parse_skill_metadata(str(valid_skill)) is not None

    invalid_metadata = parse_skill_metadata(str(invalid_skill))
    assert invalid_metadata is not None
    assert invalid_metadata.get("error", {}).get("file_path") == str(invalid_skill)
    assert "missing required field 'description'" in invalid_metadata.get("error", {}).get("validation_errors", [])

    assert parse_skill_metadata(str(non_skill)) is None

    manager = SkillManager(skills_dir=str(tmp_path))
    manager.refresh_skills()

    listed = manager.list_skills()
    assert "test-skill" in listed
    assert "broken" not in listed


def test_hot_reloader_skips_duplicate_version_events(tmp_path: Path):
    skill_dir = tmp_path / "dup"
    skill_dir.mkdir()
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(_valid_skill_md(), encoding="utf-8")

    reloader = SkillHotReloader()
    nacos_calls: list[tuple[str, dict]] = []
    matrix_messages: list[str] = []

    reloader.hiclaw.nacos_register = lambda service_name, metadata: nacos_calls.append((service_name, metadata)) or True
    reloader.matrix.send_to_room = lambda room, message: matrix_messages.append(message)

    event = SimpleNamespace(src_path=str(skill_file), is_directory=False)
    reloader.on_modified(event)
    reloader.on_modified(event)

    assert len(nacos_calls) == 1
    assert len(matrix_messages) == 1
    assert "ADDED" in matrix_messages[0]


def test_hot_reloader_ignores_invalid_metadata(tmp_path: Path):
    skill_dir = tmp_path / "bad"
    skill_dir.mkdir()
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text("---\nname: only-name\n---\n", encoding="utf-8")

    reloader = SkillHotReloader()
    nacos_calls: list[tuple[str, dict]] = []
    matrix_messages: list[str] = []
    reloader.hiclaw.nacos_register = lambda service_name, metadata: nacos_calls.append((service_name, metadata)) or True
    reloader.matrix.send_to_room = lambda room, message: matrix_messages.append(message)

    reloader.on_modified(SimpleNamespace(src_path=str(skill_file), is_directory=False))

    assert nacos_calls == []
    assert matrix_messages == []


def test_hiclaw_register_retry_success(monkeypatch):
    client = HiClawClient()
    attempts = {"count": 0}

    class DummyResponse:
        def raise_for_status(self):
            return None

    def _post(*args, **kwargs):
        attempts["count"] += 1
        if attempts["count"] < 2:
            raise RuntimeError("temporary")
        return DummyResponse()

    monkeypatch.setattr("src.infrastructure.registry.skill_registry.httpx.post", _post)
    monkeypatch.setattr("src.infrastructure.registry.skill_registry.time.sleep", lambda *_: None)

    assert client.nacos_register("skill.test", {"version": "1.0.0"}, retries=3, retry_delay=0) is True
    assert attempts["count"] == 2


def test_hiclaw_register_retry_failure_and_matrix_failure_notice(tmp_path: Path, monkeypatch):
    skill_dir = tmp_path / "fail"
    skill_dir.mkdir()
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(_valid_skill_md(), encoding="utf-8")

    reloader = SkillHotReloader()
    monkeypatch.setattr(
        reloader.hiclaw,
        "nacos_register",
        lambda service_name, metadata: False,
    )

    messages: list[str] = []
    reloader.matrix.send_to_room = lambda room, message: messages.append(message)

    reloader.on_modified(SimpleNamespace(src_path=str(skill_file), is_directory=False))

    assert len(messages) == 1
    assert "FAILED" in messages[0]


def test_fixture_driven_adapters_cover_native_and_external_formats():
    fixtures = [
        {"repo": "native-repo", "path": "tests/fixtures/skills/native/SKILL.md", "adapter_type": "native"},
        {"repo": "json-repo", "path": "tests/fixtures/skills/git_repo_a/skill.json", "adapter_type": "repo_skill_json"},
        {"repo": "manifest-repo", "path": "tests/fixtures/skills/git_repo_b/manifest.md", "adapter_type": "repo_manifest_yaml"},
        {"repo": "default-native", "path": "tests/fixtures/skills/native/SKILL.md"},
    ]

    adapters = SkillAdapterRegistry()
    manifest = SkillProvenanceManifest()

    for entry in fixtures:
        result = adapt_and_validate(entry, adapters, manifest)
        assert result.accepted is True
        assert result.canonical is not None

    assert len(manifest.records) == 4
    assert all(record["accepted"] for record in manifest.records)


def test_adapter_failure_is_rejected_and_provenance_recorded(tmp_path: Path):
    broken_file = tmp_path / "broken.json"
    broken_file.write_text('{"skill_name": "oops"}', encoding="utf-8")

    adapters = SkillAdapterRegistry()
    manifest = SkillProvenanceManifest()
    result = adapt_and_validate({"repo": "broken", "path": str(broken_file), "adapter_type": "repo_skill_json"}, adapters, manifest)

    assert result.accepted is False
    assert result.diagnostics
    assert manifest.records[-1]["accepted"] is False
    assert manifest.records[-1]["repo"] == "broken"


def test_parse_skill_metadata_with_adapter_type_includes_provenance():
    metadata = parse_skill_metadata("tests/fixtures/skills/git_repo_a/skill.json", adapter_type="repo_skill_json", repo="json-repo")

    assert metadata is not None
    assert metadata["name"] == "fixture-json"
    assert metadata["adapter_type"] == "repo_skill_json"
    assert metadata["provenance"]["accepted"] is True


def test_external_ingestion_requires_pinned_sha(monkeypatch):
    from src.infrastructure.registry.external_skill_ingestion import ExternalSkillIngestionError, ingest_external_skill_sources

    monkeypatch.setattr("src.infrastructure.registry.external_skill_ingestion.EXTERNAL_SKILL_SOURCES", [])
    # No configured sources should be a no-op.
    assert ingest_external_skill_sources() == []

    from src.settings import ExternalSkillSource

    monkeypatch.setattr(
        "src.infrastructure.registry.external_skill_ingestion.EXTERNAL_SKILL_SOURCES",
        [ExternalSkillSource(name="cyberstrike", repo_url="https://example.com/repo.git", pinned_ref="main", enabled=True)],
    )

    try:
        ingest_external_skill_sources()
        assert False, "expected ExternalSkillIngestionError"
    except ExternalSkillIngestionError as exc:
        assert "pinned commit SHA" in str(exc)
