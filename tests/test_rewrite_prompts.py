from app.rewrite_prompts import build_rewrite_prompt


def test_build_rewrite_prompt_contains_resume():
    prompt = build_rewrite_prompt(
        resume_text="Built a Flask application.",
    )

    assert "Built a Flask application." in prompt


def test_build_rewrite_prompt_contains_job_description():
    prompt = build_rewrite_prompt(
        resume_text="Built a Flask application.",
        job_description="Looking for Python and Flask experience.",
    )

    assert "Looking for Python and Flask experience." in prompt


def test_build_rewrite_prompt_contains_tailoring_plan():
    tailoring_plan = {
        "priorities": [
            {
                "type": "skill",
                "item": "Flask",
            }
        ]
    }

    prompt = build_rewrite_prompt(
        resume_text="Built a Flask application.",
        tailoring_plan=tailoring_plan,
    )

    assert "Flask" in prompt


def test_prompt_prevents_fabrication():
    prompt = build_rewrite_prompt(
        resume_text="Built a Flask application.",
    )

    assert "Never invent skills" in prompt
    assert "Do not fabricate numbers" in prompt
    assert "Do not create experience" in prompt


def test_prompt_requires_grounding_validation():
    prompt = build_rewrite_prompt(
        resume_text="Built a Flask application.",
    )

    assert "unsupported_claims" in prompt
    assert "grounding_status" in prompt
    assert "meaning_preserved" in prompt


def test_prompt_requires_structured_output():
    prompt = build_rewrite_prompt(
        resume_text="Built a Flask application.",
    )

    assert "structured JSON-compatible data" in prompt
    assert "summary" in prompt
    assert "experience" in prompt
    assert "projects" in prompt
    assert "skills" in prompt
    assert "validation" in prompt