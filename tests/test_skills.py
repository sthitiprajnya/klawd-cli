from pathlib import Path

from src.domain.arap.skill_parser import parse_skill_frontmatter, validate_skill_schema
from src.domain.skills import SkillManager
from src.infrastructure.registry.skill_registry import parse_skill_metadata


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


def test_parse_valid_skill_schema():
    frontmatter = parse_skill_frontmatter(_valid_skill_md())
    is_valid, errors = validate_skill_schema(frontmatter)

    assert is_valid is True
    assert errors == []


def test_reject_missing_required_fields():
    invalid = """---
name: bad-skill
version: 1.0.0
---
# Bad Skill
"""
    frontmatter = parse_skill_frontmatter(invalid)
    is_valid, errors = validate_skill_schema(frontmatter)

    assert is_valid is False
    assert "missing required field 'description'" in errors
    assert "missing required field 'triggers'" in errors


def test_registry_and_manager_skip_invalid_skill_files(tmp_path: Path):
    valid_dir = tmp_path / "valid"
    valid_dir.mkdir()
    valid_skill = valid_dir / "SKILL.md"
    valid_skill.write_text(_valid_skill_md(), encoding="utf-8")

    invalid_dir = tmp_path / "invalid"
    invalid_dir.mkdir()
    invalid_skill = invalid_dir / "SKILL.md"
    invalid_skill.write_text("---\nname: broken\n---\n", encoding="utf-8")

    non_skill = tmp_path / "README.md"
    non_skill.write_text("not a skill", encoding="utf-8")

    assert parse_skill_metadata(str(valid_skill)) is not None
    assert parse_skill_metadata(str(invalid_skill)) is None
    assert parse_skill_metadata(str(non_skill)) is None

    manager = SkillManager(skills_dir=str(tmp_path))
    manager.refresh_skills()

    listed = manager.list_skills()
    assert "test-skill" in listed
    assert "broken" not in listed
