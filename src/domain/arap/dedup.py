import httpx
from sentence_transformers import SentenceTransformer, util

from src.domain.arap.skill_parser import parse_skill_sections
from src.settings import settings

# Initialize local offline embedding model
model = SentenceTransformer("all-mpnet-base-v2")


def _search_mempalace_similarity(query: str) -> float | None:
    try:
        response = httpx.post(
            f"{settings.mempalace_base_url}/api/v1/search/similarity",
            json={"query": query, "top_k": 1},
            timeout=2.0,
        )
        if response.status_code != 200:
            return None
        payload = response.json()
        results = payload.get("results", []) if isinstance(payload, dict) else []
        if not results:
            return 0.0
        return float(results[0].get("score", 0.0))
    except Exception:
        return None

def compute_overlap(new_skill_md: str, existing_skill_md: str) -> float:
    mempalace_score = _search_mempalace_similarity(new_skill_md)
    if mempalace_score is not None:
        return mempalace_score

    new_sections   = parse_skill_sections(new_skill_md)
    exist_sections = parse_skill_sections(existing_skill_md)
    scores  = []
    weights = {"api_surface": 0.5, "usage_examples": 0.3, "concepts": 0.2}

    for section, weight in weights.items():
        if section in new_sections and section in exist_sections:
            emb_new   = model.encode(new_sections[section])
            emb_exist = model.encode(exist_sections[section])
            scores.append(weight * float(util.cos_sim(emb_new, emb_exist)))

    return sum(scores) if scores else 0.0

def dedup_decision(overlap: float) -> str:
    if overlap >= settings.dedup_similarity_threshold:
        return "MERGE"
    if overlap >= 0.60:
        return "EXTEND"
    if overlap >= 0.40:
        return "LINK"
    return "ADD"
