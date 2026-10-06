from app.resume_section_orderer import (
    DEFAULT_SECTION_ORDER,
    calculate_section_order_score,
    get_default_order,
    order_sections,
)


def test_default_order_contains_expected_sections():
    assert get_default_order() == (
        DEFAULT_SECTION_ORDER
    )


def test_fresher_order_prioritizes_projects_and_skills():
    order = get_default_order("fresher")

    assert order.index("projects") < order.index(
        "experience"
    )

    assert order.index("skills") < order.index(
        "experience"
    )


def test_experience_relevance_increases_order_score():
    low = calculate_section_order_score(
        "experience",
        relevance_score=20,
    )

    high = calculate_section_order_score(
        "experience",
        relevance_score=90,
    )

    assert high > low


def test_unknown_section_has_safe_score():
    score = calculate_section_order_score(
        "unknown",
        relevance_score=50,
    )

    assert 0 <= score <= 100


def test_experienced_candidate_favors_experience():
    order = order_sections(
        [
            "projects",
            "experience",
            "skills",
        ],
        relevance_scores={
            "projects": 50,
            "experience": 50,
            "skills": 50,
        },
        experience_level="experienced",
    )

    assert order[0] == "experience"


def test_fresher_candidate_favors_projects():
    order = order_sections(
        [
            "experience",
            "projects",
            "skills",
        ],
        relevance_scores={
            "experience": 50,
            "projects": 50,
            "skills": 50,
        },
        experience_level="fresher",
    )

    assert order[0] == "projects"


def test_relevant_project_can_beat_experience():
    order = order_sections(
        [
            "experience",
            "projects",
        ],
        relevance_scores={
            "experience": 40,
            "projects": 100,
        },
        experience_level="experienced",
    )

    assert order[0] == "projects"


def test_unavailable_sections_are_removed():
    order = order_sections(
        [
            "summary",
            "skills",
            "experience",
            "projects",
        ],
        available_sections={
            "summary": True,
            "skills": True,
            "experience": False,
            "projects": True,
        },
    )

    assert "experience" not in order
    assert "summary" in order
    assert "skills" in order
    assert "projects" in order


def test_duplicate_sections_are_removed():
    order = order_sections(
        [
            "summary",
            "skills",
            "skills",
            "experience",
            "summary",
        ]
    )

    assert order.count("skills") == 1
    assert order.count("summary") == 1


def test_empty_section_names_are_removed():
    order = order_sections(
        [
            "",
            None,
            "skills",
            "experience",
        ]
    )

    assert "" not in order
    assert None not in order


def test_section_names_are_case_insensitive():
    order = order_sections(
        [
            "SKILLS",
            "EXPERIENCE",
        ],
        relevance_scores={
            "skills": 50,
            "experience": 50,
        },
    )

    assert len(order) == 2


def test_ties_preserve_original_order():
    sections = [
        "unknown_a",
        "unknown_b",
        "unknown_c",
    ]

    order = order_sections(
        sections,
        relevance_scores={
            "unknown_a": 50,
            "unknown_b": 50,
            "unknown_c": 50,
        },
    )

    assert order == sections


def test_preserve_user_order():
    sections = [
        "projects",
        "education",
        "experience",
        "skills",
    ]

    order = order_sections(
        sections,
        relevance_scores={
            "experience": 100,
            "projects": 10,
        },
        preserve_user_order=True,
    )

    assert order == sections


def test_available_sections_accepts_list():
    order = order_sections(
        [
            "summary",
            "skills",
            "experience",
        ],
        available_sections=[
            "summary",
            "skills",
        ],
    )

    assert order == [
        "skills",
        "summary",
    ]


def test_custom_section_priority_is_supported():
    custom_priority = {
        "projects": 1.0,
        "experience": 0.5,
    }

    projects_score = calculate_section_order_score(
        "projects",
        relevance_score=80,
        section_priority=custom_priority,
    )

    experience_score = calculate_section_order_score(
        "experience",
        relevance_score=80,
        section_priority=custom_priority,
    )

    assert projects_score > experience_score


def test_order_sections_does_not_mutate_input():
    sections = [
        "projects",
        "experience",
        "skills",
    ]

    original = list(sections)

    order_sections(
        sections,
        relevance_scores={
            "experience": 100,
            "projects": 20,
        },
    )

    assert sections == original


def test_empty_sections_return_empty_list():
    assert order_sections([]) == []


def test_invalid_relevance_scores_are_safe():
    order = order_sections(
        [
            "experience",
            "projects",
        ],
        relevance_scores={
            "experience": "invalid",
            "projects": None,
        },
    )

    assert len(order) == 2