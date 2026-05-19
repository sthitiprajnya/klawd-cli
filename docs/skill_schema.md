# SKILL.md Schema

Every skill file must be named `SKILL.md` and start with YAML frontmatter.

## Required frontmatter keys

- `name` (string, non-empty)
- `description` (string, non-empty)
- `triggers` (non-empty list)
- `dependencies` (non-empty list)
- `version` (string, non-empty)
- `author` (string, non-empty)
- `license` (string, non-empty)

## Valid example

```md
---
name: fetch-docs
description: Pull and summarize official API docs
triggers:
  - docs
  - api
dependencies:
  - requests
version: 1.2.0
author: platform-team
license: MIT
---
# Fetch Docs Skill
```

## Invalid examples

### Missing required fields

```md
---
name: broken-skill
version: 0.1.0
---
```

### Wrong types

```md
---
name: broken-skill
description: bad
triggers: docs
dependencies:
  - requests
version: 0.1.0
author: team
license: MIT
---
```

### Empty lists

```md
---
name: broken-skill
description: bad
triggers: []
dependencies: []
version: 0.1.0
author: team
license: MIT
---
```
