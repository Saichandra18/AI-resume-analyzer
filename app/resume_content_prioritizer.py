"""Deterministic prioritization of final resume content."""

from copy import deepcopy


DEFAULT_SECTION_WEIGHTS = {
    "experience": 1.00,
    "projects": 0.90,
    "skills": 0.85,
    "summary": 0.80,
    "education": 0.70,
    "certifications": 0.65,
}


def _normalize_score(value):
    """Normalize a numeric score to the 0-100 range."""

    try:
        score = float(value)
    except (TypeError, ValueError):
        score = 0.0

    return max(0.0, min(100.0, score))


def _normalize_section(section):
    """Normalize a section name."""

    if section is None:
        return ""

    return str(section).strip().lower()


def calculate_priority_score(
    relevance_score=0,
    section="",
    section_weights=None,
    quality_score=0,
):
    """
    Calculate a deterministic priority score.

    Priority combines:
    - JD/content relevance: 60%
    - content quality: 20%
    - section importance: 20%
    """

    section_weights = (
        section_weights
        if section_weights is not None
        else DEFAULT_SECTION_WEIGHTS
    )

    relevance = _normalize_score(relevance_score)
    quality = _normalize_score(quality_score)

    normalized_section = _normalize_section(section)

    section_weight = section_weights.get(
        normalized_section,
        0.50,
    )

    section_score = _normalize_score(
        section_weight * 100
    )

    score = (
        relevance * 0.60
        + quality * 0.20
        + section_score * 0.20
    )

    return round(
        max(0.0, min(100.0, score)),
        2,
    )


def prioritize_content(
    items,
    section,
    relevance_scores=None,
    quality_scores=None,
    section_weights=None,
):
    """
    Prioritize content items within a resume section.

    Returns a new list and never mutates the input.

    Each result contains:
        item
        section
        priority_score
        original_index
    """

    items = deepcopy(items or [])
    relevance_scores = relevance_scores or {}
    quality_scores = quality_scores or {}

    prioritized = []

    for index, item in enumerate(items):
        priority_score = calculate_priority_score(
            relevance_score=relevance_scores.get(
                index,
                0,
            ),
            quality_score=quality_scores.get(
                index,
                0,
            ),
            section=section,
            section_weights=section_weights,
        )

        prioritized.append(
            {
                "item": item,
                "section": section,
                "priority_score": priority_score,
                "original_index": index,
            }
        )

    prioritized.sort(
        key=lambda entry: (
            -entry["priority_score"],
            entry["original_index"],
        )
    )

    return prioritized


def prioritize_sections(
    sections,
    section_weights=None,
    relevance_scores=None,
):
    """
    Prioritize resume sections.

    `sections` may be a list of section names.

    Optional `relevance_scores` can provide a section-level
    relevance score for each section name.
    """

    sections = list(sections or [])
    section_weights = (
        section_weights
        if section_weights is not None
        else DEFAULT_SECTION_WEIGHTS
    )
    relevance_scores = relevance_scores or {}

    ranked = []

    for index, section in enumerate(sections):
        normalized_section = _normalize_section(
            section
        )

        base_weight = section_weights.get(
            normalized_section,
            0.50,
        )

        relevance = _normalize_score(
            relevance_scores.get(
                normalized_section,
                base_weight * 100,
            )
        )

        score = round(
            (relevance * 0.70)
            + (base_weight * 100 * 0.30),
            2,
        )

        ranked.append(
            {
                "section": section,
                "priority_score": score,
                "original_index": index,
            }
        )

    ranked.sort(
        key=lambda entry: (
            -entry["priority_score"],
            entry["original_index"],
        )
    )

    return ranked