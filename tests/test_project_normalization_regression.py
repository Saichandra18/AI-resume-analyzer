from app.resume_generation_pipeline import _normalize_projects


def test_project_title_and_description_are_separated():
    rewritten = [
        {
            "description": (
                "AI Resume Analyzer - Built a comprehensive "
                "AI-powered platform for analyzing and optimizing resumes."
            ),
            "bullets": [],
        }
    ]

    original = [
        "AI Resume Analyzer",
        "Built an AI-powered resume analysis and optimization platform.",
    ]

    result = _normalize_projects(
        rewritten,
        original_items=original,
    )

    assert len(result) == 1
    assert result[0]["title"] == "AI Resume Analyzer"
    assert result[0]["bullets"]
    assert any(
        "optimizing" in bullet.lower()
        or "optimization" in bullet.lower()
        for bullet in result[0]["bullets"]
    )


def test_project_with_existing_bullets_is_preserved():
    result = _normalize_projects(
        [
            {
                "title": "AI Resume Analyzer",
                "bullets": [
                    "Built an AI-powered resume optimization platform."
                ],
            }
        ]
    )

    assert result[0]["title"] == "AI Resume Analyzer"
    assert len(result[0]["bullets"]) == 1
    assert "optimization" in result[0]["bullets"][0].lower()

def test_project_description_is_preserved_when_rewrite_returns_title_only():
    result = _normalize_projects(
        [{
            "title": "AI Resume Analyzer platform",
            "bullets": [],
        }],
        original_items=[
            "AI Resume Analyzer",
            "Built an AI-powered resume analysis and optimization platform.",
        ],
    )

    assert len(result) == 1
    assert result[0]["title"] == "AI Resume Analyzer"
    assert result[0]["bullets"]
    assert any(
        "optimization" in bullet.lower()
        or "optimizing" in bullet.lower()
        for bullet in result[0]["bullets"]
    )