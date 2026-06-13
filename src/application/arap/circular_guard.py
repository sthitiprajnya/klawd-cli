import networkx as nx
from dataclasses import dataclass, field
import httpx
import logging

logger = logging.getLogger("CircularGuard")

def normalize_url(url: str) -> str:
    return url.lower().strip("/")

class AbsorptionCycleError(Exception):
    pass

@dataclass
class AbsorptionNode:
    url: str
    normalized: str
    deps: list[str] = field(default_factory=list)

class CircularDependencyGuard:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.base_url = "http://mempalace:8000/api/v1/drawers"
        self._load_from_mempalace()

    def _load_from_mempalace(self):
        try:
            response = httpx.get(f"{self.base_url}/absorbed-knowledge/meta/dependency-graph", timeout=2.0)
            response.raise_for_status()
            entries = response.json().get("entries", [])
            for entry in entries:
                content = entry.get("content", {})
                if "parent" in content and "child" in content:
                    self.graph.add_edge(content["parent"], content["child"])
            logger.info("Loaded %d dependency edges from MemPalace", self.graph.number_of_edges())
        except httpx.HTTPStatusError as e:
            logger.error("MemPalace graph fetch failed with status %s", e.response.status_code)
        except Exception as e:
            logger.exception("Failed to load dependency graph from MemPalace: %s", e)

    def check_and_register(self, parent_url: str, child_url: str) -> None:
        norm_parent = normalize_url(parent_url)
        norm_child  = normalize_url(child_url)

        self.graph.add_edge(norm_parent, norm_child)
        if not nx.is_directed_acyclic_graph(self.graph):
            self.graph.remove_edge(norm_parent, norm_child)
            raise AbsorptionCycleError(f"Absorbing {norm_child} from {norm_parent} creates a cycle.")

        try:
            response = httpx.post(f"{self.base_url}/absorbed-knowledge/meta/dependency-graph", json={
                "data": {"parent": norm_parent, "child": norm_child},
                "aaak_event": "dependency-registered"
            }, timeout=2.0)
            response.raise_for_status()
            logger.info("Stored dependency edge in MemPalace: %s -> %s", norm_parent, norm_child)
        except httpx.HTTPStatusError as e:
            logger.error("MemPalace graph store failed with status %s", e.response.status_code)
        except Exception as e:
            logger.exception("Failed to store dependency graph in MemPalace: %s", e)
