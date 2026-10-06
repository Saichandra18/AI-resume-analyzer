from app.rewrite_models import (
    build_rewrite_input,
    build_rewrite_output,
)


def test_build_rewrite_input():
    result = build_rewrite_input(
        "Python developer with ML experience.",
        {"skills": ["Python", "Machine Learning"]},
        {
            "tailoring_plan": {
                "skills": []
            }
        },
        "Python machine learning developer",
    )

    assert result["resume_text"] == (
        "Python developer with ML experience."
    )

    assert result["resume_data"] == {
        "skills": ["Python", "Machine Learning"]
    }

    assert result["tailoring_plan"] == {
        "tailoring_plan": {
            "skills": []
        }
    }

    assert result["job_description"] == (
        "Python machine learning developer"
    )


def test_build_rewrite_input_handles_missing_values():
    result = build_rewrite_input(None)

    assert result == {
        "resume_text": "",
        "resume_data": {},
        "tailoring_plan": {},
        "job_description": "",
    }


def test_build_rewrite_output():
    result = build_rewrite_output(
        summary={
            "original": "Python developer.",
            "rewritten": "Python-focused developer.",
        },
        experience=[
            {
                "original": "Worked with Python.",
                "rewritten": (
                    "Developed solutions using Python."
                ),
            }
        ],
        projects=[],
        skills={},
        validation={
            "meaning_preserved": True,
            "unsupported_claims": [],
            "grounding_status": "verified",
        },
    )

    assert result["summary"]["rewritten"] == (
        "Python-focused developer."
    )

    assert len(result["experience"]) == 1

    assert result["validation"]["meaning_preserved"] is True


def test_build_rewrite_output_has_safe_defaults():
    result = build_rewrite_output()

    assert result["summary"] == {}
    assert result["experience"] == []
    assert result["projects"] == []
    assert result["skills"] == {}

    assert result["validation"] == {
        "meaning_preserved": False,
        "unsupported_claims": [],
        "grounding_status": "unverified",
    }