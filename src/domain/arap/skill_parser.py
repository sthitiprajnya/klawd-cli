import re
from typing import Any

import yaml

REQUIRED_SKILL_FIELDS = {
    "name": str,
    "description": str,
    "triggers": list,
    "dependencies": list,
    "version": str,
    "author": str,
    "license": str,
}


def parse_skill_frontmatter(skill_md: str) -> dict[str, Any]:
    match = re.match(r"^---\n(.*?)\n---\n", skill_md, re.DOTALL)
    if not match:
        return {}
    try:
        parsed = yaml.safe_load(match.group(1)) or {}
        return parsed if isinstance(parsed, dict) else {}
    except yaml.YAMLError:
        return {}


def extract_yaml_field(skill_md: str, field: str) -> Any:
    return parse_skill_frontmatter(skill_md).get(field)


def validate_skill_schema(frontmatter: dict[str, Any]) -> tuple[bool, list[str]]:
    errors: list[str] = []

    for field, expected_type in REQUIRED_SKILL_FIELDS.items():
        value = frontmatter.get(field)
        if value is None:
            errors.append(f"missing required field '{field}'")
            continue

        if not isinstance(value, expected_type):
            errors.append(
                f"field '{field}' must be of type {expected_type.__name__}, got {type(value).__name__}"
            )
            continue

        if expected_type is str and not value.strip():
            errors.append(f"field '{field}' must not be empty")
        if expected_type is list and len(value) == 0:
            errors.append(f"field '{field}' must not be empty")

    return len(errors) == 0, errors


SECTION_HEADERS = {
    "api_surface": r"##\s+API Surface",
    "usage_examples": r"##\s+Usage Examples",
    "concepts": r"##\s+Integration Pattern",
    "limitations": r"##\s+Known Limitations",
    "conflict_history": r"##\s+Conflict History",
}


def parse_skill_sections(skill_md: str) -> dict[str, str]:
    body = re.sub(r"^---\n.*?\n---\n", "", skill_md, flags=re.DOTALL)
    sections = {}
    header_positions = []

    for key, pattern in SECTION_HEADERS.items():
        for match in re.finditer(pattern, body, re.MULTILINE | re.IGNORECASE):
            header_positions.append((match.start(), key, match.end()))

    header_positions.sort()
    for i, (_, key, end) in enumerate(header_positions):
        next_start = header_positions[i + 1][0] if i + 1 < len(header_positions) else len(body)
        sections[key] = body[end:next_start].strip()

    return sections
