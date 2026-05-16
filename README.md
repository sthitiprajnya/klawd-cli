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
