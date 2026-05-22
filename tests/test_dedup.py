import pytest
from unittest.mock import patch, MagicMock

from src.domain.arap.dedup import compute_overlap, dedup_decision

def get_mock_skill_md(api_surface="API", usage_examples="Usage", concepts="Concepts"):
    md = "---\nname: mock\n---\n"
    if api_surface:
        md += f"## API Surface\n{api_surface}\n"
    if usage_examples:
        md += f"## Usage Examples\n{usage_examples}\n"
    if concepts:
        md += f"## Integration Pattern\n{concepts}\n"
    return md

@patch("src.domain.arap.dedup._search_mempalace_similarity")
def test_compute_overlap_with_mempalace_score(mock_search):
    mock_search.return_value = 0.85
    new_md = get_mock_skill_md()
    exist_md = get_mock_skill_md()

    score = compute_overlap(new_md, exist_md)
    assert score == 0.85
    mock_search.assert_called_once_with(new_md)

@patch("src.domain.arap.dedup._search_mempalace_similarity")
@patch("src.domain.arap.dedup.model.encode")
@patch("src.domain.arap.dedup.util.cos_sim")
def test_compute_overlap_fallback_local_calculation(mock_cos_sim, mock_encode, mock_search):
    mock_search.return_value = None
    mock_cos_sim.return_value = 0.8
    mock_encode.return_value = [0.1, 0.2]

    new_md = get_mock_skill_md()
    exist_md = get_mock_skill_md()

    score = compute_overlap(new_md, exist_md)

    # weights are api_surface: 0.5, usage_examples: 0.3, concepts: 0.2
    # sum of weights is 1.0. 1.0 * 0.8 = 0.8
    assert pytest.approx(score) == 0.8

    assert mock_encode.call_count == 6 # 3 sections * 2 (new and exist)
    assert mock_cos_sim.call_count == 3

@patch("src.domain.arap.dedup._search_mempalace_similarity")
def test_compute_overlap_no_overlapping_sections(mock_search):
    mock_search.return_value = None

    new_md = get_mock_skill_md(usage_examples=None, concepts=None) # Only API surface
    exist_md = get_mock_skill_md(api_surface=None, concepts=None) # Only Usage examples

    score = compute_overlap(new_md, exist_md)

    assert score == 0.0

@patch("src.domain.arap.dedup._search_mempalace_similarity")
@patch("src.domain.arap.dedup.model.encode")
@patch("src.domain.arap.dedup.util.cos_sim")
def test_compute_overlap_partial_overlapping_sections(mock_cos_sim, mock_encode, mock_search):
    mock_search.return_value = None
    mock_cos_sim.return_value = 1.0
    mock_encode.return_value = [0.1]

    new_md = get_mock_skill_md(concepts=None) # API surface, Usage examples
    exist_md = get_mock_skill_md(usage_examples=None) # API surface, concepts

    score = compute_overlap(new_md, exist_md)

    # Only API surface overlaps, weight is 0.5
    assert pytest.approx(score) == 0.5
    assert mock_encode.call_count == 2
    assert mock_cos_sim.call_count == 1
