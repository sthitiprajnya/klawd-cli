# OmniAgent Enterprise 🧠

OmniAgent is a highly advanced, fully autonomous software engineering AI agent. Designed to operate 24/7, it combines the structural roles of a software company with dynamic capability absorption and an intelligent, multi-provider model routing engine.

**Note:** This agent is strictly configured for benign software engineering (refactoring, architecture, documentation) and explicitly refuses to ingest, create, or execute offensive security or hacking tools.

## Architecture

This application is built using Domain-Driven Design (DDD):
- **src/domain**: Agents (Planner, Engineer, Reviewer, Absorber) and Skill definitions.
- **src/infrastructure**: SQLAlchemy Database (Memory and Job Queues) and the intelligent NIMRouter (balances Kimi, Minimax, GLM over Nvidia NIM).
- **src/application**: Autonomous execution workflows implementing the Hermes self-evolution loop and GStack logic.
- **src/presentation**: FastAPI server and the embedded frontend dashboard (Vanilla JS/CSS).

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
Create a `.env` file:
```env
NIM_API_KEY_1=your_key_here
NIM_API_KEY_2=your_key_here
```

3. **Start the Enterprise API & Dashboard**
```bash
./run_server.sh
```
*View the dashboard at `http://localhost:8000/`*

4. **Install the Self-Evolution Daemon**
```bash
sudo cp omni_agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable omni_agent
sudo systemctl start omni_agent
```
