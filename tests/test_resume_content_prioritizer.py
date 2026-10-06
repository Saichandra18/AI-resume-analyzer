from app.resume_content_prioritizer import (
    DEFAULT_SECTION_WEIGHTS,
    calculate_priority_score,
    prioritize_content,
    prioritize_sections,
)


def test_experience_has_high_default_section_weight():
    assert (
        DEFAULT_SECTION_WEIGHTS["experience"]
        > DEFAULT_SECTION_WEIGHTS["education"]
    )


def test_priority_score_is_bounded():
    score = calculate_priority_score(
        relevance_score=100,
        quality_score=100,
        section="experience",
    )

    assert 0 <= score <= 100


def test_high_relevance_content_gets_higher_priority():
    low = calculate_priority_score(
        relevance_score=20,
        quality_score=80,
        section="experience",
    )

    high = calculate_priority_score(
        relevance_score=90,
        quality_score=80,
        section="experience",
    )

    assert high > low


def test_high_quality_content_gets_higher_priority():
    low = calculate_priority_score(
        relevance_score=80,
        quality_score=20,
        section="experience",
    )

    high = calculate_priority_score(
        relevance_score=80,
        quality_score=90,
        section="experience",
    )

    assert high > low


def test_section_weight_affects_priority():
    experience = calculate_priority_score(
        relevance_score=80,
        quality_score=80,
        section="experience",
    )

    education = calculate_priority_score(
        relevance_score=80,
        quality_score=80,
        section="education",
    )

    assert experience > education


def test_unknown_section_uses_safe_default():
    score = calculate_priority_score(
        relevance_score=80,
        quality_score=80,
        section="unknown",
    )

    assert 0 <= score <= 100


def test_prioritize_content_orders_by_score():
    items = [
        {"description": "Low relevance"},
        {"description": "High relevance"},
    ]

    prioritized = prioritize_content(
        items,
        section="experience",
        relevance_scores={
            0: 20,
            1: 90,
        },
        quality_scores={
            0: 80,
            1: 80,
        },
    )

    assert prioritized[0]["original_index"] == 1
    assert prioritized[1]["original_index"] == 0


def test_prioritize_content_is_deterministic_for_ties():
    items = [
        {"description": "A"},
        {"description": "B"},
        {"description": "C"},
    ]

    prioritized = prioritize_content(
        items,
        section="projects",
        relevance_scores={
            0: 80,
            1: 80,
            2: 80,
        },
        quality_scores={
            0: 80,
            1: 80,
            2: 80,
        },
    )

    assert [
        item["original_index"]
        for item in prioritized
    ] == [0, 1, 2]


def test_prioritize_content_preserves_section():
    prioritized = prioritize_content(
        [{"name": "Project"}],
        section="projects",
    )

    assert prioritized[0]["section"] == "projects"


def test_prioritize_content_does_not_mutate_input():
    items = [
        {
            "name": "Project",
            "skills": ["Python"],
        }
    ]

    original = [
        {
            "name": "Project",
            "skills": ["Python"],
        }
    ]

    prioritize_content(
        items,
        section="projects",
        relevance_scores={0: 90},
    )

    assert items == original


def test_prioritize_empty_content():
    assert prioritize_content(
        [],
        section="experience",
    ) == []


def test_prioritize_sections_uses_default_weights():
    sections = [
        "education",
        "experience",
        "projects",
    ]

    ranked = prioritize_sections(sections)

    assert ranked[0]["section"] == "experience"


def test_relevant_section_can_override_default_order():
    sections = [
        "experience",
        "projects",
    ]

    ranked = prioritize_sections(
        sections,
        relevance_scores={
            "experience": 50,
            "projects": 100,
        },
    )

    assert ranked[0]["section"] == "projects"


def test_section_prioritization_is_deterministic():
    sections = [
        "projects",
        "projects",
    ]

    ranked = prioritize_sections(sections)

    assert [
        item["original_index"]
        for item in ranked
    ] == [0, 1]


def test_section_names_are_case_insensitive():
    upper = calculate_priority_score(
        relevance_score=80,
        quality_score=80,
        section="EXPERIENCE",
    )

    lower = calculate_priority_score(
        relevance_score=80,
        quality_score=80,
        section="experience",
    )

    assert upper == lower


def test_invalid_scores_are_handled_safely():
    score = calculate_priority_score(
        relevance_score="invalid",
        quality_score=None,
        section="experience",
    )

    assert score >= 0


def test_custom_section_weights_are_supported():
    custom_weights = {
        "projects": 1.0,
        "experience": 0.5,
    }

    projects = calculate_priority_score(
        relevance_score=80,
        quality_score=80,
        section="projects",
        section_weights=custom_weights,
    )

    experience = calculate_priority_score(
        relevance_score=80,
        quality_score=80,
        section="experience",
        section_weights=custom_weights,
    )

    assert projects > experience