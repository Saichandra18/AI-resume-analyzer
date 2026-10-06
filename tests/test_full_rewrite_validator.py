from app.full_rewrite_validator import validate_full_rewrite


def test_full_rewrite_is_grounded_when_all_sections_are_grounded():
    result = validate_full_rewrite(
        summary={
            "validation": {
                "grounding_status": "grounded",
                "unsupported_claims": [],
            }
        },
        experience=[
            {
                "validation": {
                    "grounding_status": "grounded",
                    "unsupported_claims": [],
                }
            }
        ],
        projects=[
            {
                "validation": {
                    "grounding_status": "grounded",
                    "unsupported_claims": [],
                }
            }
        ],
        skills={
            "validation": {
                "grounding_status": "grounded",
                "unsupported_claims": [],
            }
        },
    )

    assert result["grounding_status"] == "grounded"
    assert result["meaning_preserved"] is True
    assert result["unsupported_claims"] == []
    assert result["needs_review_sections"] == []


def test_full_rewrite_detects_experience_issue():
    result = validate_full_rewrite(
        experience=[
            {
                "validation": {
                    "grounding_status": "needs_review",
                    "unsupported_claims": [
                        "New numeric claim detected: 50000"
                    ],
                }
            }
        ]
    )

    assert result["grounding_status"] == "needs_review"
    assert result["meaning_preserved"] is False
    assert "experience" in result["needs_review_sections"]
    assert (
        "New numeric claim detected: 50000"
        in result["unsupported_claims"]
    )


def test_full_rewrite_detects_project_issue():
    result = validate_full_rewrite(
        projects=[
            {
                "validation": {
                    "grounding_status": "needs_review",
                    "unsupported_claims": [
                        "New technical term detected: docker"
                    ],
                }
            }
        ]
    )

    assert result["grounding_status"] == "needs_review"
    assert "projects" in result["needs_review_sections"]


def test_full_rewrite_detects_summary_issue():
    result = validate_full_rewrite(
        summary={
            "validation": {
                "grounding_status": "needs_review",
                "unsupported_claims": [
                    "Summary response is incomplete."
                ],
            }
        }
    )

    assert result["grounding_status"] == "needs_review"
    assert "summary" in result["needs_review_sections"]


def test_full_rewrite_detects_skills_issue():
    result = validate_full_rewrite(
        skills={
            "validation": {
                "grounding_status": "needs_review",
                "unsupported_claims": [
                    "New technical term detected: aws"
                ],
            }
        }
    )

    assert result["grounding_status"] == "needs_review"
    assert "skills" in result["needs_review_sections"]


def test_full_rewrite_collects_multiple_issues():
    result = validate_full_rewrite(
        experience=[
            {
                "validation": {
                    "grounding_status": "needs_review",
                    "unsupported_claims": ["New number: 50"],
                }
            }
        ],
        projects=[
            {
                "validation": {
                    "grounding_status": "needs_review",
                    "unsupported_claims": ["New tool: Docker"],
                }
            }
        ],
    )

    assert result["grounding_status"] == "needs_review"
    assert result["meaning_preserved"] is False
    assert len(result["unsupported_claims"]) == 2
    assert "experience" in result["needs_review_sections"]
    assert "projects" in result["needs_review_sections"]


def test_full_rewrite_handles_empty_sections():
    result = validate_full_rewrite()

    assert result["grounding_status"] == "grounded"
    assert result["meaning_preserved"] is True
    assert result["unsupported_claims"] == []
    assert result["needs_review_sections"] == []

def test_full_rewrite_deduplicates_unsupported_claims():
    result = validate_full_rewrite(
        experience=[
            {
                "validation": {
                    "grounding_status": "needs_review",
                    "unsupported_claims": [
                        "New technical term detected: docker"
                    ],
                }
            }
        ],
        projects=[
            {
                "validation": {
                    "grounding_status": "needs_review",
                    "unsupported_claims": [
                        "New technical term detected: docker"
                    ],
                }
            }
        ],
    )

    assert result["grounding_status"] == "needs_review"
    assert result["unsupported_claims"] == [
        "New technical term detected: docker"
    ]
    