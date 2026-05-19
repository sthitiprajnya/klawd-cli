# OmniAgent Enterprise 🧠

OmniAgent is a highly advanced, fully autonomous software engineering AI agent. Designed to operate 24/7, it combines the structural roles of a software company with dynamic capability absorption and an intelligent, multi-provider model routing engine.

**Note:** This agent is strictly configured for benign software engineering (refactoring, architecture, documentation) and explicitly refuses to ingest, create, or execute offensive security or hacking tools.

## Enterprise Architecture (DDD)

This application is built using a clean Domain-Driven Design (DDD) architecture to ensure scalability and maintainability.

```text
omni_agent/
├── r_and_d_daemon.py          # Background worker for continuous self-evolution
├── run_server.sh              # Entry point to launch the FastAPI server
├── requirements.txt           # Python dependencies
├── omni_agent.service         # Systemd daemon configuration
├── src/
│   ├── application/           # Application logic
│   │   └── workflows.py       # Orchestrates the agents (Hermes/GStack loops)
│   ├── domain/                # Core business models
│   │   ├── agents.py          # Planner, Engineer, Reviewer, Absorber agents
│   │   └── skills.py          # Secure skill parsing and state management
│   ├── infrastructure/        # External system integrations
│   │   ├── database.py        # SQLAlchemy persistence (SQLite/MemPalace mock)
│   │   ├── llm_router.py      # Intelligent routing across NIM/GLM/Kimi/Minimax
│   │   └── skills/            # Directory where dynamically absorbed code lives
│   └── presentation/          # User interfaces and network boundaries
│       ├── api/
│       │   └── main.py        # FastAPI endpoints for jobs and memory
│       ├── static/            # Frontend assets
│       │   ├── css/style.css
│       │   └── js/app.js
│       └── templates/
│           └── index.html     # Real-time monitoring dashboard
└── tests/                     # Comprehensive pytest suite
    ├── test_api.py
    └── test_skills.py
```

## Installation (Ubuntu / Systemd)

1. **Clone and Install Dependencies**
```bash
git clone https://github.com/your-org/omni_agent.git /opt/omni_agent
cd /opt/omni_agent
sudo apt update && sudo apt install -y python3-pip python3-venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Configure Environment**
Create a `.env` file in the root directory:
```env
NIM_API_KEY_1=your_key_here
NIM_API_KEY_2=your_key_here
```

3. **Start the Enterprise API & Dashboard**
```bash
./run_server.sh
```
*You can now view the live dashboard at `http://localhost:8000/`*

4. **Install the Self-Evolution Daemon**
To make the agent truly autonomous, install the R&D daemon which continuously feeds the API with self-improvement tasks.
```bash
sudo cp omni_agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable omni_agent
sudo systemctl start omni_agent
```

Check the daemon status:
```bash
sudo systemctl status omni_agent
```

## OpenHuman Context Integration (Config + Runbook)

### Environment keys

The agent's OpenHuman JSON-RPC integration is configurable via environment variables:

- `OPENHUMAN_JSONRPC_URL` (default: `http://openhuman-core:7788/jsonrpc`)
- `OPENHUMAN_TIMEOUT_SECONDS` (default: `2.0`)
- `OPENHUMAN_MAX_RETRIES` (default: `1`, total attempts = retries + initial attempt)

### JSON-RPC dependency behavior

The base agent fetches context from OpenHuman using `memory_tree.get` and supports payload adapters for both:

- `memory_tree.get`-style responses: `{"result": {"context": "..."}}`
- `prompt.update`-style responses: `{"result": "..."}`

If OpenHuman fails (timeout, malformed payload, non-200 status), the agent **continues processing** with an explicit stateless marker:

- `[Context: Stateless fallback mode enabled (OpenHuman unavailable)]`

### Health and observability runbook

OpenHuman is treated as a **degradable dependency** for prompt context enrichment and does not hard-fail job execution.

For every review iteration, workflow metadata includes OpenHuman observability fields:

- `openhuman_available` (`true`/`false`)
- `openhuman_latency_ms` (number or `null`)
- `openhuman_error` (error classifier or `null`)
- `openhuman_attempts` (attempt count)

Operational guidance:

1. If `openhuman_available=false` and `openhuman_error=timeout`, increase `OPENHUMAN_TIMEOUT_SECONDS` or investigate network/service latency.
2. If `openhuman_error=malformed_jsonrpc_payload`, verify OpenHuman response schema compatibility.
3. If repeated failures persist, jobs will continue in stateless mode; treat this as degraded quality context, not platform outage.

## Skill Schema Validation

Skill discovery only loads files named `SKILL.md` and validates frontmatter before registration.

Required frontmatter fields:

- `name`
- `description`
- `triggers`
- `dependencies`
- `version`
- `author`
- `license`

For full schema details and examples, see `docs/skill_schema.md`.
