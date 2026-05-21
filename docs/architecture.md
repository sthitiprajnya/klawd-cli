# Architecture

This project uses Domain-Driven Design (DDD), FastAPI for the API layer, and Rust workers for CPU-intensive background tasks.

## Modules
* **Domain:** Core business logic and agents.
* **Application:** Orchestration logic and Hermes learning loop.
* **Infrastructure:** Database logic, security middleware, LLM routing, memory locking, and integrations.
* **Presentation:** The REST API, WebSockets, and HTML UI.
* **Rust Workers:** Standalone Rust HTTP services for rapid tasks.
