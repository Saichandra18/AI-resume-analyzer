"""Deterministic resume length control."""

from copy import deepcopy


DEFAULT_SECTION_LIMITS = {
    "summary": 1,
    "skills": 12,
    "experience": 6,
    "projects": 3,
    "education": 3,
    "certifications": 4,
}


DEFAULT_PAGE_CAPACITY = {
    1: 22,
    2: 40,
}


def _normalize_section(section):
    """Normalize a section name."""
    if section is None:
        return ""

    return str(section).strip().lower()


def _normalize_positive_int(value, name):
    """Validate a positive integer."""
    if not isinstance(value, int) or value < 1:
        raise ValueError(
            f"{name} must be a positive integer."
        )

    return value


def _get_priority(entry):
    """Extract a safe priority score."""
    if not isinstance(entry, dict):
        return 0.0

    try:
        return float(
            entry.get(
                "priority_score",
                entry.get("score", 0),
            )
        )
    except (TypeError, ValueError):
        return 0.0


def _rank_entries(entries):
    """
    Rank entries by priority while preserving original
    ordering for ties.
    """

    indexed = []

    for index, entry in enumerate(entries):
        indexed.append(
            (
                -_get_priority(entry),
                index,
                deepcopy(entry),
            )
        )

    indexed.sort(
        key=lambda value: (
            value[0],
            value[1],
        )
    )

    return [
        value[2]
        for value in indexed
    ]


def calculate_capacity(
    target_pages,
    page_capacity=None,
):
    """
    Return approximate content capacity for a target page count.

    This is an abstract content-unit capacity, not a physical
    PDF line/page measurement.
    """

    target_pages = _normalize_positive_int(
        target_pages,
        "target_pages",
    )

    page_capacity = (
        page_capacity
        if page_capacity is not None
        else DEFAULT_PAGE_CAPACITY
    )

    if not page_capacity:
        raise ValueError(
            "page_capacity cannot be empty."
        )

    if target_pages in page_capacity:
        return _normalize_positive_int(
            page_capacity[target_pages],
            "page capacity",
        )

    known_pages = sorted(
        page_capacity.keys()
    )

    if target_pages < known_pages[0]:
        return _normalize_positive_int(
            page_capacity[known_pages[0]],
            "page capacity",
        )

    largest_page = known_pages[-1]

    if target_pages > largest_page:
        base = _normalize_positive_int(
            page_capacity[largest_page],
            "page capacity",
        )

        return base * (
            target_pages / largest_page
        )

    lower_page = known_pages[0]

    for page in known_pages:
        if page <= target_pages:
            lower_page = page

    upper_page = known_pages[-1]

    for page in known_pages:
        if page >= target_pages:
            upper_page = page
            break

    if lower_page == upper_page:
        return page_capacity[lower_page]

    lower_capacity = page_capacity[
        lower_page
    ]
    upper_capacity = page_capacity[
        upper_page
    ]

    ratio = (
        target_pages - lower_page
    ) / (
        upper_page - lower_page
    )

    return round(
        lower_capacity
        + (
            upper_capacity
            - lower_capacity
        ) * ratio
    )


def limit_section_items(
    items,
    section,
    max_items=None,
    preserve_minimum=0,
):
    """
    Limit the number of items in one section.

    Items are prioritized before trimming when priority
    information is available.
    """

    items = deepcopy(items or [])

    if max_items is not None:
        max_items = (
            _normalize_positive_int(
                max_items,
                "max_items",
            )
        )

    if not isinstance(
        preserve_minimum,
        int,
    ) or preserve_minimum < 0:
        raise ValueError(
            "preserve_minimum must be a non-negative integer."
        )

    if preserve_minimum > len(items):
        preserve_minimum = len(items)

    if max_items is None:
        max_items = len(items)

    if max_items < preserve_minimum:
        max_items = preserve_minimum

    ranked = _rank_entries(items)

    selected = ranked[:max_items]
    excluded = ranked[max_items:]

    return {
        "section": section,
        "selected": selected,
        "excluded": excluded,
    }


def control_resume_length(
    sections,
    target_pages=1,
    section_limits=None,
    page_capacity=None,
):
    """
    Apply deterministic length limits to resume sections.

    `sections` should be a dictionary:

        {
            "experience": [...],
            "projects": [...],
            "skills": [...]
        }

    Returns selected and excluded content for every section.
    """

    sections = deepcopy(sections or {})

    target_pages = _normalize_positive_int(
        target_pages,
        "target_pages",
    )

    section_limits = (
        deepcopy(section_limits)
        if section_limits is not None
        else deepcopy(DEFAULT_SECTION_LIMITS)
    )

    capacity = calculate_capacity(
        target_pages,
        page_capacity=page_capacity,
    )

    result = {
        "target_pages": target_pages,
        "capacity": capacity,
        "sections": {},
    }

    total_selected = 0

    for section, items in sections.items():
        normalized = _normalize_section(
            section
        )

        limit = section_limits.get(
            normalized
        )

        if limit is not None:
            limit = max(
                0,
                int(limit),
            )

        limited = limit_section_items(
            items=items,
            section=section,
            max_items=limit,
        )

        result["sections"][section] = limited

        total_selected += len(
            limited["selected"]
        )

    result["total_selected"] = (
        total_selected
    )

    result["over_capacity"] = (
        total_selected > capacity
    )

    return result