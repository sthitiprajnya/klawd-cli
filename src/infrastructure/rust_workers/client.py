from __future__ import annotations

import os
from dataclasses import dataclass

import httpx

from .errors import RustWorkerError, RustWorkerTimeoutError, RustWorkerValidationError


@dataclass(frozen=True)
class RustEndpoint:
    base_url: str
    timeout_seconds: float


class RustWorkerClient:
    def __init__(self) -> None:
        self.probe = RustEndpoint(os.getenv("RUST_PROBE_URL", "http://rust-provider-prober:8081"), 1.5)
        self.skill = RustEndpoint(os.getenv("RUST_SKILL_URL", "http://rust-skill-ingestor:8082"), 2.0)
        self.event = RustEndpoint(os.getenv("RUST_EVENT_URL", "http://rust-event-normalizer:8083"), 1.0)

    def get_provider_status(self, pool: str, keys: list[str]) -> dict[str, bool]:
        payload = {"model_pool": pool, "providers": [{"api_key": k} for k in keys]}
        body = self._request(self.probe, "/v1/probe/providers", payload)
        return {item["api_key"]: item["available"] for item in body["providers"]}

    def _request(self, endpoint: RustEndpoint, path: str, payload: dict) -> dict:
        try:
            response = httpx.post(f"{endpoint.base_url}{path}", json=payload, timeout=endpoint.timeout_seconds)
        except httpx.TimeoutException as exc:
            raise RustWorkerTimeoutError(str(exc)) from exc
        except httpx.HTTPError as exc:
            raise RustWorkerError(str(exc)) from exc

        if response.status_code == 422:
            raise RustWorkerValidationError(response.text)
        if response.status_code >= 400:
            raise RustWorkerError(f"HTTP {response.status_code}: {response.text}")
        return response.json()
