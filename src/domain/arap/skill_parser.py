import re
import yaml
from typing import Any

def parse_skill_frontmatter(skill_md: str) -> dict:
    match = re.match(r"^---\n(.*?)\n---\n", skill_md, re.DOTALL)
    if not match: return {}
    try: return yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError: return {}

def extract_yaml_field(skill_md: str, field: str) -> Any:
    return parse_skill_frontmatter(skill_md).get(field)

SECTION_HEADERS = {
    "api_surface":       r"##\s+API Surface",
    "usage_examples":    r"##\s+Usage Examples",
    "concepts":          r"##\s+Integration Pattern",
    "limitations":       r"##\s+Known Limitations",
    "conflict_history":  r"##\s+Conflict History",
}

def parse_skill_sections(skill_md: str) -> dict[str, str]:
    body = re.sub(r"^---\n.*?\n---\n", "", skill_md, flags=re.DOTALL)
    sections = {}
    header_positions = []

    for key, pattern in SECTION_HEADERS.items():
        for match in re.finditer(pattern, body, re.MULTILINE | re.IGNORECASE):
            header_positions.append((match.start(), key, match.end()))

    header_positions.sort()
    for i, (start, key, end) in enumerate(header_positions):
        next_start = header_positions[i + 1][0] if i + 1 < len(header_positions) else len(body)
        sections[key] = body[end:next_start].strip()

    return sections