import networkx as nx
from dataclasses import dataclass, field

# --- Mocks for valid execution ---
class MemPalaceMock:
    def search_hall(self, **kwargs): return []
    def store(self, **kwargs): pass
mempalace = MemPalaceMock()

def normalize_url(url: str) -> str: return url.lower().strip("/")
class AbsorptionCycleError(Exception): pass
# ---------------------------------

@dataclass
class AbsorptionNode:
    url: str
    normalized: str
    deps: list[str] = field(default_factory=list)

class CircularDependencyGuard:
    def __init__(self):
        self.graph = nx.DiGraph()
        self._load_from_mempalace()

    def _load_from_mempalace(self):
        entries = mempalace.search_hall(wing="absorbed-knowledge", hall="dependency-graph")
        for entry in entries:
            self.graph.add_edge(entry.get("parent"), entry.get("child"))

    def check_and_register(self, parent_url: str, child_url: str) -> None:
        norm_parent = normalize_url(parent_url)
        norm_child  = normalize_url(child_url)

        self.graph.add_edge(norm_parent, norm_child)
        if not nx.is_directed_acyclic_graph(self.graph):
            self.graph.remove_edge(norm_parent, norm_child)
            raise AbsorptionCycleError(f"Absorbing {norm_child} from {norm_parent} creates a cycle.")

        mempalace.store(
            wing="absorbed-knowledge", room="meta", hall="dependency-graph",
            content={"parent": norm_parent, "child": norm_child},
            aaak_event="dependency-registered"
        )