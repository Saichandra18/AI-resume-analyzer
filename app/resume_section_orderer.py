"""Deterministic section ordering for final resumes."""

from copy import deepcopy

DEFAULT_SECTION_ORDER = [
    "summary",
    "skills",
    "experience",
    "projects",
    "education",
    "certifications",
]

DEFAULT_SECTION_PRIORITY = {
    "experience": 1.00,
    "projects": 0.90,
    "skills": 0.85,
    "summary": 0.80,
    "education": 0.70,
    "certifications": 0.65,
}


def _normalize_section(section):
    """Normalize a section name for comparisons."""
    if section is None:
        return ""

    return str(section).strip().lower()


def _normalize_score(value):
    """Normalize a score to 0-100."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        value = 0.0

    return max(0.0, min(100.0, value))


def _is_available(section, available_sections):
    """Check whether a section contains usable content."""

    if available_sections is None:
        return True

    if isinstance(available_sections, dict):
        value = available_sections.get(section)

        if isinstance(value, bool):
            return value

        return bool(value)

    normalized = {
        _normalize_section(item)
        for item in available_sections
    }

    return section in normalized


def calculate_section_order_score(
    section,
    relevance_score=0,
    experience_level="experienced",
    section_priority=None,
):
    """
    Calculate a deterministic ordering score.

    The score combines:
    - JD relevance
    - section importance
    - candidate experience profile
    """

    section_priority = (
        section_priority
        if section_priority is not None
        else DEFAULT_SECTION_PRIORITY
    )

    normalized_section = _normalize_section(section)
    relevance = _normalize_score(relevance_score)

    base_priority = section_priority.get(
        normalized_section,
        0.50,
    )

    base_score = base_priority * 100

    level = _normalize_section(
        experience_level
    )

    # Freshers generally benefit from projects and skills
    # appearing more prominently.
    if level in {
        "fresher",
        "student",
        "entry-level",
        "entry level",
    }:
        if normalized_section == "projects":
            base_score += 15
        elif normalized_section == "skills":
            base_score += 10
        elif normalized_section == "experience":
            base_score -= 10

    # Experienced candidates generally benefit from
    # experience appearing prominently.
    elif level in {
        "experienced",
        "professional",
        "mid-level",
        "mid level",
        "senior",
    }:
        if normalized_section == "experience":
            base_score += 10
        elif normalized_section == "projects":
            base_score -= 5

    return round(
        (relevance * 0.60)
        + (base_score * 0.40),
        2,
    )


def order_sections(
    sections,
    relevance_scores=None,
    available_sections=None,
    experience_level="experienced",
    section_priority=None,
    preserve_user_order=False,
):
    """
    Return sections ordered for final resume composition.

    Empty/unavailable sections are removed when availability
    information is supplied.

    The input is never mutated.
    """

    sections = deepcopy(sections or [])
    relevance_scores = relevance_scores or {}

    normalized_sections = []

    seen = set()

    for index, section in enumerate(sections):
        normalized = _normalize_section(section)

        if not normalized:
            continue

        if normalized in seen:
            continue

        seen.add(normalized)

        if not _is_available(
            normalized,
            available_sections,
        ):
            continue

        normalized_sections.append(
            {
                "section": section,
                "normalized": normalized,
                "original_index": index,
            }
        )

    if preserve_user_order:
        return [
            item["section"]
            for item in normalized_sections
        ]

    ranked = []

    for item in normalized_sections:
        normalized = item["normalized"]

        score = calculate_section_order_score(
            section=normalized,
            relevance_score=relevance_scores.get(
                normalized,
                0,
            ),
            experience_level=experience_level,
            section_priority=section_priority,
        )

        ranked.append(
            {
                "section": item["section"],
                "priority_score": score,
                "original_index": item[
                    "original_index"
                ],
            }
        )

    ranked.sort(
        key=lambda item: (
            -item["priority_score"],
            item["original_index"],
        )
    )

    return [
        item["section"]
        for item in ranked
    ]


def get_default_order(
    experience_level="experienced",
):
    """Return a sensible default section order."""

    if _normalize_section(
        experience_level
    ) in {
        "fresher",
        "student",
        "entry-level",
        "entry level",
    }:
        return [
            "summary",
            "skills",
            "projects",
            "experience",
            "education",
            "certifications",
        ]

    return list(DEFAULT_SECTION_ORDER)