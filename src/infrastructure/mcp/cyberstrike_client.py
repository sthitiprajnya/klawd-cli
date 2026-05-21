from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from typing import Any

import httpx

try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
except ImportError:  # pragma: no cover - optional runtime dependency
    Ed25519PrivateKey = None  # type: ignore[assignment]
    serialization = None  # type: ignore[assignment]


@dataclass(frozen=True)
class CyberstrikeSession:
    session_id: str
    public_key: str


@dataclass(frozen=True)
class TaxonomyEntry:
    id: str
    name: str
    framework: str
    metadata: dict[str, Any]


class CyberstrikeClientError(RuntimeError):
    pass


class CyberstrikeClient:
    def __init__(
        self,
        base_url: str | None = None,
        private_key_pem: str | None = None,
        timeout_seconds: float = 10.0,
    ) -> None:
        self.base_url = base_url or os.getenv("CYBERSTRIKE_BOLT_URL", "http://cyberstrike-bolt:8888")
        self.private_key_pem = private_key_pem or os.getenv("CYBERSTRIKE_ED25519_PRIVATE_KEY", "")
        self.timeout_seconds = timeout_seconds
        self._session: CyberstrikeSession | None = None

    def bootstrap_session(self) -> CyberstrikeSession:
        challenge_payload = self._request("GET", "/bolt/auth/challenge")
        challenge = str(challenge_payload.get("challenge", ""))
        if not challenge:
            raise CyberstrikeClientError("missing auth challenge from bolt endpoint")

        signature_b64, public_key_b64 = self._sign_challenge(challenge)
        session_payload = self._request(
            "POST",
            "/bolt/auth/session",
            payload={"challenge": challenge, "signature": signature_b64, "public_key": public_key_b64},
        )
        session_id = str(session_payload.get("session_id", ""))
        if not session_id:
            raise CyberstrikeClientError("missing session_id in bolt auth response")

        self._session = CyberstrikeSession(session_id=session_id, public_key=public_key_b64)
        return self._session

    def query_cis_controls(self, version: str = "v8") -> list[TaxonomyEntry]:
        payload = self._request("GET", f"/bolt/taxonomy/cis?version={version}", with_session=True)
        return self._taxonomy_entries(payload)

    def query_mitre_techniques(self, tactic: str | None = None) -> list[TaxonomyEntry]:
        query = f"?tactic={tactic}" if tactic else ""
        payload = self._request("GET", f"/bolt/taxonomy/mitre{query}", with_session=True)
        return self._taxonomy_entries(payload)

    def _taxonomy_entries(self, payload: dict[str, Any]) -> list[TaxonomyEntry]:
        items = payload.get("items", [])
        entries: list[TaxonomyEntry] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            entries.append(
                TaxonomyEntry(
                    id=str(item.get("id", "")),
                    name=str(item.get("name", "")),
                    framework=str(item.get("framework", "")),
                    metadata=item.get("metadata", {}) if isinstance(item.get("metadata", {}), dict) else {},
                )
            )
        return entries

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        *,
        with_session: bool = False,
    ) -> dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        if with_session:
            if not self._session:
                self.bootstrap_session()
            headers["X-Bolt-Session"] = self._session.session_id

        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        try:
            response = httpx.request(method=method, url=url, json=payload or {}, headers=headers, timeout=self.timeout_seconds)
        except httpx.HTTPError as exc:
            raise CyberstrikeClientError(f"cyberstrike request failed: {exc}") from exc

        if response.status_code >= 400:
            raise CyberstrikeClientError(f"cyberstrike HTTP {response.status_code}: {response.text}")
        body = response.json() if response.content else {}
        if not isinstance(body, dict):
            raise CyberstrikeClientError("unexpected non-object response from cyberstrike-bolt")
        return body

    def _sign_challenge(self, challenge: str) -> tuple[str, str]:
        if Ed25519PrivateKey is None or serialization is None:
            raise CyberstrikeClientError(
                "cryptography package is required for Ed25519 auth; install 'cryptography' dependency"
            )
        if not self.private_key_pem:
            raise CyberstrikeClientError("missing CYBERSTRIKE_ED25519_PRIVATE_KEY for Bolt session bootstrap")

        private_key = serialization.load_pem_private_key(self.private_key_pem.encode("utf-8"), password=None)
        if not isinstance(private_key, Ed25519PrivateKey):
            raise CyberstrikeClientError("configured key is not an Ed25519 private key")

        signature = private_key.sign(challenge.encode("utf-8"))
        public_key = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        return base64.b64encode(signature).decode("utf-8"), base64.b64encode(public_key).decode("utf-8")
