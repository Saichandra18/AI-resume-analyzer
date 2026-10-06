from app.rag.optimization.resume_context import (
    ResumeContextBuilder,
)


def test_builder_returns_empty_context_for_none():
    builder = ResumeContextBuilder()

    result = builder.build(None)

    assert result == {
        "summary": "",
        "skills": [],
        "experience": [],
        "projects": [],
        "education": [],
        "certifications": [],
    }


def test_builder_rejects_invalid_resume_data():
    builder = ResumeContextBuilder()

    try:
        builder.build("invalid")
    except TypeError as exc:
        assert "resume_data" in str(exc)
    else:
        raise AssertionError(
            "Expected TypeError."
        )


def test_builder_preserves_resume_content():
    builder = ResumeContextBuilder()

    resume = {
        "summary": "Python backend developer",
        "skills": [
            "Python",
            "Flask",
        ],
        "experience": [
            {
                "job_title": "Backend Developer",
                "company": "Example",
                "bullets": [
                    "Built REST APIs"
                ],
            }
        ],
        "projects": [
            {
                "title": "Resume Analyzer",
                "bullets": [
                    "Built Flask application"
                ],
            }
        ],
        "education": [
            {
                "degree": "B.Tech"
            }
        ],
        "certifications": [
            "AWS Certified"
        ],
    }

    result = builder.build(resume)

    assert result["summary"] == (
        "Python backend developer"
    )
    assert result["skills"] == [
        "Python",
        "Flask",
    ]
    assert result["experience"][0][
        "job_title"
    ] == "Backend Developer"
    assert result["projects"][0][
        "title"
    ] == "Resume Analyzer"


def test_builder_does_not_mutate_resume():
    builder = ResumeContextBuilder()

    resume = {
        "skills": [
            "Python"
        ],
        "experience": [
            {
                "job_title": "Developer"
            }
        ],
    }

    original = {
        "skills": [
            "Python"
        ],
        "experience": [
            {
                "job_title": "Developer"
            }
        ],
    }

    builder.build(resume)

    assert resume == original


def test_to_query_text_contains_candidate_content():
    builder = ResumeContextBuilder()

    context = builder.build(
        {
            "summary": "Python backend developer",
            "skills": [
                "Python",
                "Flask",
            ],
            "projects": [
                {
                    "title": "API Platform",
                    "bullets": [
                        "Built REST APIs"
                    ],
                }
            ],
        }
    )

    query_text = builder.to_query_text(
        context
    )

    assert "Python backend developer" in query_text
    assert "Python" in query_text
    assert "Flask" in query_text
    assert "API Platform" in query_text
    assert "Built REST APIs" in query_text


def test_to_query_text_is_deterministic():
    builder = ResumeContextBuilder()

    context = builder.build(
        {
            "skills": [
                "Python",
                "Flask",
            ],
            "experience": [
                {
                    "company": "Example",
                    "job_title": "Developer",
                }
            ],
        }
    )

    first = builder.to_query_text(context)
    second = builder.to_query_text(context)

    assert first == second