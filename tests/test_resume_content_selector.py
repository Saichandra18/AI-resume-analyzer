from app.resume_content_selector import (
    rank_content,
    score_content,
    select_content,
)


def test_relevant_content_scores_higher():
    relevant = {
        "description": (
            "Built Python machine learning models "
            "using SQL."
        )
    }

    irrelevant = {
        "description": (
            "Designed marketing posters and "
            "social media campaigns."
        )
    }

    relevant_score = score_content(
        relevant,
        target_keywords=[
            "python",
            "machine learning",
            "sql",
        ],
        target_skills=[
            "python",
            "machine learning",
        ],
    )

    irrelevant_score = score_content(
        irrelevant,
        target_keywords=[
            "python",
            "machine learning",
            "sql",
        ],
        target_skills=[
            "python",
            "machine learning",
        ],
    )

    assert relevant_score > irrelevant_score


def test_skill_overlap_increases_score():
    base = {
        "description": "Developed software applications."
    }

    matching = {
        "description": (
            "Developed Python software applications."
        )
    }

    base_score = score_content(
        base,
        target_skills=["python"],
    )

    matching_score = score_content(
        matching,
        target_skills=["python"],
    )

    assert matching_score > base_score


def test_keyword_overlap_increases_score():
    base = {
        "description": "Developed applications."
    }

    matching = {
        "description": (
            "Developed machine learning applications."
        )
    }

    base_score = score_content(
        base,
        target_keywords=["machine learning"],
    )

    matching_score = score_content(
        matching,
        target_keywords=["machine learning"],
    )

    assert matching_score > base_score


def test_relevance_score_affects_result():
    item = {
        "description": "Software development project."
    }

    low = score_content(
        item,
        relevance_score=20,
    )

    high = score_content(
        item,
        relevance_score=90,
    )

    assert high > low


def test_rank_content_returns_highest_score_first():
    items = [
        {
            "description": "Marketing campaign."
        },
        {
            "description": (
                "Python machine learning project."
            )
        },
    ]

    ranked = rank_content(
        items,
        target_keywords=[
            "python",
            "machine learning",
        ],
        target_skills=["python"],
    )

    assert ranked[0]["original_index"] == 1
    assert ranked[1]["original_index"] == 0


def test_ranking_is_deterministic_for_ties():
    items = [
        {"description": "Project A"},
        {"description": "Project B"},
        {"description": "Project C"},
    ]

    ranked = rank_content(items)

    assert [
        entry["original_index"]
        for entry in ranked
    ] == [0, 1, 2]


def test_select_content_respects_max_items():
    items = [
        {"description": "Project A"},
        {"description": "Project B"},
        {"description": "Project C"},
    ]

    result = select_content(
        items,
        max_items=2,
    )

    assert len(result["selected"]) == 2
    assert len(result["excluded"]) == 1


def test_select_content_with_zero_limit():
    items = [
        {"description": "Project A"},
        {"description": "Project B"},
    ]

    result = select_content(
        items,
        max_items=0,
    )

    assert result["selected"] == []
    assert len(result["excluded"]) == 2


def test_empty_content_is_supported():
    assert rank_content([]) == []

    result = select_content([])

    assert result == {
        "selected": [],
        "excluded": [],
    }


def test_invalid_max_items_is_rejected():
    try:
        select_content(
            [{"description": "Project"}],
            max_items=-1,
        )
    except ValueError as exc:
        assert "max_items" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_selector_does_not_mutate_input():
    items = [
        {
            "description": "Python project",
            "skills": ["Python"],
        }
    ]

    original = [
        {
            "description": "Python project",
            "skills": ["Python"],
        }
    ]

    select_content(
        items,
        target_skills=["python"],
    )

    assert items == original


def test_score_is_bounded():
    score = score_content(
        {
            "description": (
                "Python machine learning SQL AWS Docker "
                "React Java C++"
            )
        },
        target_keywords=[
            "python",
            "machine learning",
            "sql",
            "aws",
            "docker",
        ],
        target_skills=[
            "python",
            "machine learning",
            "sql",
            "aws",
            "docker",
        ],
        relevance_score=100,
    )

    assert 0 <= score <= 100


def test_string_items_are_supported():
    score = score_content(
        "Python machine learning project",
        target_skills=["python"],
    )

    assert score > 0