from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(frozen=True)
class HexstrikeToolIntent:
    """Metadata describing intended tool behavior for PRISM checks."""

    name: str
    destructive: bool = False
    reason: str | None = None

    def as_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {
            "X-Tool-Intent": self.name,
            "X-Tool-Destructive": "true" if self.destructive else "false",
        }
        if self.reason:
            headers["X-Tool-Reason"] = self.reason
        return headers


@dataclass(frozen=True)
class HexstrikeResponse:
    status_code: int
    data: dict[str, Any]


class HexstrikeClientError(RuntimeError):
    pass


class HexstrikeClient:
    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        api_key_header: str = "Authorization",
        timeout_seconds: float = 10.0,
    ) -> None:
        self.base_url = base_url or os.getenv("HEXSTRIKE_BASE_URL", "http://hexstrike-server:8888")
        self.api_key = api_key or os.getenv("HEXSTRIKE_API_KEY")
        self.api_key_header = api_key_header
        self.timeout_seconds = timeout_seconds

    def call_endpoint(
        self,
        path: str,
        payload: dict[str, Any] | None = None,
        *,
        method: str = "POST",
        intent: HexstrikeToolIntent | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> HexstrikeResponse:
        headers = self._build_headers(intent=intent, extra_headers=extra_headers)
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

        try:
            response = httpx.request(
                method=method,
                url=url,
                json=payload or {},
                headers=headers,
                timeout=self.timeout_seconds,
            )
        except httpx.HTTPError as exc:
            raise HexstrikeClientError(f"hexstrike request failed: {exc}") from exc

        if response.status_code >= 400:
            raise HexstrikeClientError(f"hexstrike HTTP {response.status_code}: {response.text}")

        body = response.json() if response.content else {}
        if not isinstance(body, dict):
            body = {"result": body}
        return HexstrikeResponse(status_code=response.status_code, data=body)

    def _build_headers(
        self,
        *,
        intent: HexstrikeToolIntent | None,
        extra_headers: dict[str, str] | None,
    ) -> dict[str, str]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.api_key:
            headers[self.api_key_header] = self.api_key
        if intent:
            headers.update(intent.as_headers())
        if extra_headers:
            headers.update(extra_headers)
        return headers
