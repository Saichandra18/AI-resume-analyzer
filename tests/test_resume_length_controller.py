from app.resume_length_controller import (
    DEFAULT_PAGE_CAPACITY,
    DEFAULT_SECTION_LIMITS,
    calculate_capacity,
    control_resume_length,
    limit_section_items,
)


def test_default_section_limits_exist():
    assert DEFAULT_SECTION_LIMITS["experience"] > 0
    assert DEFAULT_SECTION_LIMITS["projects"] > 0
    assert DEFAULT_SECTION_LIMITS["skills"] > 0


def test_default_page_capacity_exists():
    assert DEFAULT_PAGE_CAPACITY[1] > 0
    assert DEFAULT_PAGE_CAPACITY[2] > (
        DEFAULT_PAGE_CAPACITY[1]
    )


def test_one_page_capacity_is_available():
    capacity = calculate_capacity(1)

    assert capacity == DEFAULT_PAGE_CAPACITY[1]


def test_two_page_capacity_is_available():
    capacity = calculate_capacity(2)

    assert capacity == DEFAULT_PAGE_CAPACITY[2]


def test_larger_page_count_increases_capacity():
    one_page = calculate_capacity(1)
    two_pages = calculate_capacity(2)
    three_pages = calculate_capacity(3)

    assert two_pages > one_page
    assert three_pages > two_pages


def test_invalid_target_pages_are_rejected():
    for value in [0, -1, "1", None]:
        try:
            calculate_capacity(value)
        except ValueError:
            pass
        else:
            raise AssertionError(
                "Expected ValueError"
            )


def test_limit_section_items_respects_limit():
    items = [
        {"item": "A", "priority_score": 10},
        {"item": "B", "priority_score": 90},
        {"item": "C", "priority_score": 50},
    ]

    result = limit_section_items(
        items,
        section="projects",
        max_items=2,
    )

    assert len(result["selected"]) == 2
    assert len(result["excluded"]) == 1


def test_limit_section_items_keeps_highest_priority():
    items = [
        {"item": "Low", "priority_score": 10},
        {"item": "High", "priority_score": 90},
        {"item": "Medium", "priority_score": 50},
    ]

    result = limit_section_items(
        items,
        section="projects",
        max_items=1,
    )

    assert result["selected"][0]["item"] == "High"


def test_limit_section_items_preserves_tie_order():
    items = [
        {"item": "A", "priority_score": 50},
        {"item": "B", "priority_score": 50},
        {"item": "C", "priority_score": 50},
    ]

    result = limit_section_items(
        items,
        section="projects",
        max_items=2,
    )

    assert [
        item["item"]
        for item in result["selected"]
    ] == ["A", "B"]


def test_limit_section_items_preserves_minimum():
    items = [
        {"item": "A", "priority_score": 90},
        {"item": "B", "priority_score": 80},
        {"item": "C", "priority_score": 70},
    ]

    result = limit_section_items(
        items,
        section="experience",
        max_items=1,
        preserve_minimum=2,
    )

    assert len(result["selected"]) == 2


def test_limit_section_items_does_not_mutate_input():
    items = [
        {"item": "A", "priority_score": 10},
        {"item": "B", "priority_score": 90},
    ]

    original = [
        {"item": "A", "priority_score": 10},
        {"item": "B", "priority_score": 90},
    ]

    limit_section_items(
        items,
        section="projects",
        max_items=1,
    )

    assert items == original


def test_limit_section_items_empty_input():
    result = limit_section_items(
        [],
        section="projects",
        max_items=3,
    )

    assert result["selected"] == []
    assert result["excluded"] == []


def test_no_limit_keeps_all_items():
    items = [
        {"item": "A"},
        {"item": "B"},
    ]

    result = limit_section_items(
        items,
        section="projects",
    )

    assert len(result["selected"]) == 2
    assert result["excluded"] == []


def test_control_resume_length_processes_sections():
    sections = {
        "experience": [
            {"item": "A", "priority_score": 90},
            {"item": "B", "priority_score": 80},
        ],
        "projects": [
            {"item": "P1", "priority_score": 70},
            {"item": "P2", "priority_score": 60},
        ],
    }

    result = control_resume_length(
        sections,
        target_pages=1,
        section_limits={
            "experience": 1,
            "projects": 1,
        },
    )

    assert len(
        result["sections"]["experience"]["selected"]
    ) == 1

    assert len(
        result["sections"]["projects"]["selected"]
    ) == 1


def test_control_resume_length_reports_total_selected():
    sections = {
        "experience": [
            {"item": "A"},
            {"item": "B"},
        ],
        "projects": [
            {"item": "P1"},
        ],
    }

    result = control_resume_length(
        sections,
        target_pages=1,
        section_limits={
            "experience": 1,
            "projects": 1,
        },
    )

    assert result["total_selected"] == 2


def test_control_resume_length_reports_capacity():
    result = control_resume_length(
        {},
        target_pages=1,
    )

    assert (
        result["capacity"]
        == DEFAULT_PAGE_CAPACITY[1]
    )


def test_control_resume_length_detects_over_capacity():
    sections = {
        "experience": [
            {"item": str(i)}
            for i in range(30)
        ]
    }

    result = control_resume_length(
        sections,
        target_pages=1,
        section_limits={
            "experience": 30,
        },
    )

    assert result["over_capacity"] is True


def test_control_resume_length_does_not_mutate_input():
    sections = {
        "projects": [
            {
                "item": "Project",
                "priority_score": 90,
            }
        ]
    }

    original = {
        "projects": [
            {
                "item": "Project",
                "priority_score": 90,
            }
        ]
    }

    control_resume_length(
        sections,
        target_pages=1,
    )

    assert sections == original


def test_empty_resume_is_supported():
    result = control_resume_length(
        {},
        target_pages=1,
    )

    assert result["sections"] == {}
    assert result["total_selected"] == 0
    assert result["over_capacity"] is False


def test_unknown_sections_are_supported():
    sections = {
        "custom_section": [
            {"item": "Custom"}
        ]
    }

    result = control_resume_length(
        sections,
        target_pages=1,
    )

    assert (
        "custom_section"
        in result["sections"]
    )