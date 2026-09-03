# Klawd-CLI Architecture Design

This document outlines a recommended architecture for `klawd-cli`, a standard Python CLI application that integrates orchestration/task-routing with a hardware/execution module.

## 1. Recommended Directory Structure

For a standard Python CLI application, a clean and modular directory structure is crucial. We recommend a `src/` layout to prevent import issues and clearly separate the application logic from configuration and tests.

```text
klawd-cli/
├── src/
│   └── klawd_cli/
│       ├── __init__.py
│       ├── cli.py               # Main CLI entry point (e.g., using argparse, click, or typer)
│       ├── core/
│       │   ├── __init__.py
│       │   ├── orchestrator.py  # Orchestration and task-routing logic (inspired by prime-agent)
│       │   └── command.py       # Data structures/models for commands
│       └── execution/
│           ├── __init__.py
│           └── executor.py      # Hardware and execution logic (inspired by openvidia)
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_orchestrator.py
│   └── test_executor.py
├── pyproject.toml               # Modern dependency management and project metadata
├── README.md
└── .gitignore
```

## 2. Python Class Interfaces

This example demonstrates how an `Orchestrator` can parse and route a command, safely passing it to an `Executor` using standard Python dataclasses for clean data transfer.

```python
from dataclasses import dataclass
from typing import Optional, Dict, Any

# --- Command Models ---

@dataclass
class ParsedCommand:
    """Represents a validated and parsed command ready for execution."""
    action: str
    target: str
    parameters: Dict[str, Any]
    timeout_seconds: Optional[int] = None

# --- Execution Module ---

class Executor:
    """
    Hardware and execution module.
    Responsible for executing the specific action safely on the target environment.
    """
    def __init__(self, hardware_config: Dict[str, Any]):
        self.config = hardware_config
        # Initialize hardware connections or sandboxed environments here

    def execute(self, command: ParsedCommand) -> bool:
        """
        Executes the parsed command.
        Returns True on success, False otherwise.
        """
        print(f"[Executor] Starting execution of action: {command.action}")
        print(f"[Executor] Target: {command.target}, Params: {command.parameters}")

        # Implementation of actual hardware execution or sub-process calling goes here
        # E.g., if command.action == "run_model":
        #     self._run_on_gpu(command.target, command.parameters)

        return True

# --- Orchestration Module ---

class Orchestrator:
    """
    Orchestration and task-routing module.
    Responsible for parsing raw input, validating it, and routing to the executor.
    """
    def __init__(self, executor: Executor):
        self.executor = executor

    def route_task(self, raw_input: str) -> None:
        """
        Parses raw CLI input, validates it, and routes to the executor.
        """
        print(f"[Orchestrator] Received raw input: {raw_input}")

        # 1. Parse and validate input (Simplified example)
        # In reality, this might involve complex LLM parsing or strict CLI argument parsing.
        command = ParsedCommand(
            action="evaluate_model",
            target="local_gpu_0",
            parameters={"batch_size": 32, "model_path": "/models/llama3"}
        )

        print("[Orchestrator] Task parsed successfully. Routing to Executor...")

        # 2. Pass to Executor safely
        success = self.executor.execute(command)

        if success:
            print("[Orchestrator] Task completed successfully.")
        else:
            print("[Orchestrator] Task failed.")

# --- Example Usage ---
# if __name__ == "__main__":
#     executor = Executor(hardware_config={"gpu_enabled": True})
#     orchestrator = Orchestrator(executor=executor)
#     orchestrator.route_task("run evaluation on local gpu")
```

## 3. Dependency Management Best Practices

For integrating complex modules (like ML/hardware execution and agentic orchestration), managing dependencies cleanly is critical to avoid "dependency hell".

1. **Use Modern Build Tools (Poetry or UV):**
   Instead of `requirements.txt`, use `pyproject.toml` with a tool like [Poetry](https://python-poetry.org/) or [uv](https://github.com/astral-sh/uv). These tools resolve dependencies strictly and generate lock files (`poetry.lock` or `uv.lock`) ensuring deterministic builds across environments.

2. **Isolate Environments:**
   Always develop inside a virtual environment. Both Poetry and UV manage virtual environments automatically. Never install project dependencies to the global system Python.

3. **Separate Dependency Groups:**
   Use groups in your `pyproject.toml` to separate core runtime dependencies from development tools.
   ```toml
   [tool.poetry.dependencies]
   python = "^3.10"
   click = "^8.1.7"
   pydantic = "^2.5.3"

   [tool.poetry.group.dev.dependencies]
   pytest = "^8.0.0"
   ruff = "^0.2.0"
   ```

4. **Pin Hardware-Specific Libraries Carefully:**
   Libraries interacting with hardware (like CUDA/PyTorch for the Execution module) often have strict version requirements. Define these explicitly, or use optional extras if the CLI can run in a "lightweight" mode without them.

5. **Interface Segregation:**
   Keep the dependencies for the Orchestrator (e.g., LLM clients, agent frameworks) entirely decoupled from the Executor dependencies (e.g., CUDA, GPU drivers) within the code structure. The `ParsedCommand` dataclass acts as the clean boundary between them.
