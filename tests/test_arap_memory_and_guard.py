from unittest.mock import MagicMock

import httpx

from src.application.arap.circular_guard import CircularDependencyGuard
from src.domain.arap.dedup import dedup_decision, compute_overlap


def test_dedup_threshold_edges(monkeypatch):
    monkeypatch.setattr("src.domain.arap.dedup.settings.dedup_similarity_threshold", 0.8)
    assert dedup_decision(0.8) == "MERGE"
    assert dedup_decision(0.79) == "EXTEND"


def test_mempalace_outage_falls_back_to_local_similarity(monkeypatch):
    monkeypatch.setattr("src.domain.arap.dedup._search_mempalace_similarity", lambda _q: None)
    monkeypatch.setattr("src.domain.arap.dedup.parse_skill_sections", lambda _s: {"api_surface": "x"})
    monkeypatch.setattr("src.domain.arap.dedup.model", MagicMock(encode=lambda _x: [1.0]))
    monkeypatch.setattr("src.domain.arap.dedup.util.cos_sim", lambda _a, _b: 1.0)

    assert compute_overlap("new", "existing") == 0.5


def test_stale_graph_fetch_is_observable_and_nonfatal(monkeypatch):
    class StaleResponse:
        status_code = 503

        def raise_for_status(self):
            raise httpx.HTTPStatusError("stale", request=MagicMock(), response=self)

    monkeypatch.setattr("src.application.arap.circular_guard.httpx.get", lambda *_a, **_k: StaleResponse())

    guard = CircularDependencyGuard()
    assert guard.graph.number_of_edges() == 0
