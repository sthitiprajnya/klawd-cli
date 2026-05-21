import pytest
import httpx

from src.infrastructure.rust_workers.client import RustWorkerClient
from src.infrastructure.rust_workers.errors import RustWorkerTimeoutError, RustWorkerValidationError


class DummyResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload
        self.text = str(payload)

    def json(self):
        return self._payload


def test_provider_probe_contract_success(monkeypatch):
    def fake_post(_url, json=None, timeout=None):
        assert json["model_pool"] == "default"
        assert timeout == 1.5
        return DummyResponse(200, {"providers": [{"api_key": "k1", "available": True}]})

    monkeypatch.setattr("src.infrastructure.rust_workers.client.httpx.post", fake_post)
    c = RustWorkerClient()
    assert c.get_provider_status("default", ["k1"]) == {"k1": True}


def test_deterministic_error_mapping_validation(monkeypatch):
    monkeypatch.setattr(
        "src.infrastructure.rust_workers.client.httpx.post",
        lambda *_a, **_k: DummyResponse(422, {"error": "bad schema"}),
    )
    c = RustWorkerClient()
    with pytest.raises(RustWorkerValidationError):
        c.get_provider_status("default", ["k1"])


def test_deterministic_error_mapping_transport(monkeypatch):
    def fake_post(*_a, **_k):
        raise httpx.TimeoutException("timeout")

    monkeypatch.setattr("src.infrastructure.rust_workers.client.httpx.post", fake_post)
    c = RustWorkerClient()
    with pytest.raises(RustWorkerTimeoutError):
        c.get_provider_status("default", ["k1"])
