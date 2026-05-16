# OmniAgent Enterprise 🧠

OmniAgent is a highly advanced, fully autonomous software engineering AI agent. Designed to operate 24/7, it combines the structural roles of a software company with dynamic capability absorption and an intelligent, multi-provider model routing engine.

**Note:** This agent is strictly configured for benign software engineering (refactoring, architecture, documentation) and explicitly refuses to ingest, create, or execute offensive security or hacking tools.

## Architecture & Mindset

OmniAgent is inspired by the bleeding-edge of agentic workflows:
- **Intelligent NIM Routing**: Balances up to 5 API keys and routes logic intelligently. It leverages **GLM-4-plus** for deep coding tasks, **Kimi (Moonshot 128k)** for massive repository context parsing, and **Minimax** for fast routing.
- **Hermes Self-Evolution**: The agent features a continuous Reviewer-to-Engineer reflection loop. It critiques its own output, iterates, and stores meta-lessons in long-term memory.
- **GStack Autonomy**: OmniAgent is orchestrated into distinct sub-agents (Planner, Engineer, Reviewer, Absorber) working cohesively to resolve complex pipelines without human supervision.
- **Deerflow Pipeline Execution**: Tasks are broken down into pipelines (DAGs) rather than linear scripts, ensuring robust edge-case handling.
- **Majin Buu Absorption**: Can ingest open-source code repositories and extract their AST contexts to dynamically add new "skills" to its permanent repository.

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
Create a `.env` file in the root directory and add your API keys:
```env
NIM_API_KEY_1=your_key_here
NIM_API_KEY_2=your_key_here
```

3. **Start the Enterprise API & Dashboard**
```bash
./run_server.sh
```
*You can now view the dashboard at `http://localhost:8000/`*

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
