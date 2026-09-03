from app.resume_tailoring import generate_tailoring_plan


def test_returns_empty_plan_for_empty_input():
    result = generate_tailoring_plan(
        {},
        {},
        {},
        {},
    )

    assert result == {
        "tailoring_plan": {
            "priorities": [],
            "summary": [],
            "skills": [],
            "experience": [],
            "keywords": [],
            "qualifications": [],
            "warnings": [
                (
                    "Only add skills or experience that accurately "
                    "reflect your background."
                ),
                (
                    "Do not fabricate employment history, "
                    "qualifications, achievements, or metrics."
                ),
                (
                    "Use job-specific keywords naturally rather "
                    "than keyword stuffing."
                ),
            ],
        }
    }


def test_returns_empty_plan_for_none_input():
    result = generate_tailoring_plan(
        None,
        None,
        None,
        None,
    )

    assert result == {
        "tailoring_plan": {
            "priorities": [],
            "summary": [],
            "skills": [],
            "experience": [],
            "keywords": [],
            "qualifications": [],
            "warnings": [
                (
                    "Only add skills or experience that accurately "
                    "reflect your background."
                ),
                (
                    "Do not fabricate employment history, "
                    "qualifications, achievements, or metrics."
                ),
                (
                    "Use job-specific keywords naturally rather "
                    "than keyword stuffing."
                ),
            ],
        }
    }


def test_generates_missing_skill_tailoring():
    ats_result = {
        "missing_skills": ["MLOps"],
        "missing_qualifications": [],
        "missing_keywords": [],
        "experience": {},
    }

    result = generate_tailoring_plan(
        {},
        ats_result,
        {},
        {},
    )

    skills = result["tailoring_plan"]["skills"]

    assert len(skills) == 1

    suggestion = skills[0]

    assert suggestion["type"] == "skill"
    assert suggestion["item"] == "MLOps"
    assert suggestion["action"] == "highlight"
    assert suggestion["priority"] in {
        "high",
        "medium",
        "low",
    }
    assert "MLOps" in suggestion["recommendation"]
    assert "applicable" in suggestion["recommendation"].lower()


def test_generates_missing_keyword_tailoring():
    ats_result = {
        "missing_skills": [],
        "missing_qualifications": [],
        "missing_keywords": ["model validation"],
        "experience": {},
    }

    result = generate_tailoring_plan(
        {},
        ats_result,
        {},
        {},
    )

    keywords = result["tailoring_plan"]["keywords"]

    assert len(keywords) == 1

    suggestion = keywords[0]

    assert suggestion["type"] == "keyword"
    assert suggestion["item"] == "model validation"
    assert suggestion["action"] == "incorporate"
    assert "model validation" in (
        suggestion["recommendation"].lower()
    )
    assert "applicable" in (
        suggestion["recommendation"].lower()
    )


def test_generates_missing_qualification_tailoring():
    ats_result = {
        "missing_skills": [],
        "missing_qualifications": [
            "Master's degree"
        ],
        "missing_keywords": [],
        "experience": {},
    }

    result = generate_tailoring_plan(
        {},
        ats_result,
        {},
        {},
    )

    qualifications = (
        result["tailoring_plan"]["qualifications"]
    )

    assert len(qualifications) == 1

    suggestion = qualifications[0]

    assert suggestion["type"] == "qualification"
    assert suggestion["item"] == "Master's degree"
    assert suggestion["action"] == "highlight"
    assert "master's degree" in (
        suggestion["recommendation"].lower()
    )
    assert "applicable" in (
        suggestion["recommendation"].lower()
    )


def test_generates_experience_alignment_when_requirement_is_met():
    ats_result = {
        "missing_skills": [],
        "missing_qualifications": [],
        "missing_keywords": [],
        "experience": {
            "required_years": 2,
            "candidate_years": 4,
            "meets_requirement": True,
        },
    }

    result = generate_tailoring_plan(
        {},
        ats_result,
        {},
        {},
    )

    experience = (
        result["tailoring_plan"]["experience"]
    )

    assert len(experience) == 1

    suggestion = experience[0]

    assert suggestion["type"] == "experience"
    assert suggestion["action"] == "strengthen"
    assert suggestion["priority"] == "high"
    assert "relevant" in (
        suggestion["recommendation"].lower()
    )


def test_generates_honest_experience_gap_when_requirement_is_not_met():
    ats_result = {
        "missing_skills": [],
        "missing_qualifications": [],
        "missing_keywords": [],
        "experience": {
            "required_years": 3,
            "candidate_years": 1,
            "meets_requirement": False,
        },
    }

    result = generate_tailoring_plan(
        {},
        ats_result,
        {},
        {},
    )

    experience = (
        result["tailoring_plan"]["experience"]
    )

    assert len(experience) == 1

    suggestion = experience[0]

    assert suggestion["type"] == "experience"
    assert suggestion["action"] == "review"
    assert suggestion["priority"] == "high"

    recommendation = (
        suggestion["recommendation"].lower()
    )

    assert "do not misrepresent" in recommendation
    assert "relevant" in recommendation


def test_generates_summary_tailoring_guidance():
    resume_data = {
        "summary": [
            "Python developer with AI experience."
        ]
    }

    ats_result = {
        "missing_skills": [],
        "missing_qualifications": [],
        "missing_keywords": [],
        "experience": {},
    }

    result = generate_tailoring_plan(
        resume_data,
        ats_result,
        {},
        {},
    )

    summary = result["tailoring_plan"]["summary"]

    assert len(summary) == 1

    suggestion = summary[0]

    assert suggestion["type"] == "summary"
    assert suggestion["action"] == "strengthen"
    assert suggestion["priority"] == "high"
    assert "target" in (
        suggestion["recommendation"].lower()
    )


def test_generates_priorities_from_tailoring_actions():
    ats_result = {
        "missing_skills": ["MLOps"],
        "missing_qualifications": [],
        "missing_keywords": ["model validation"],
        "experience": {
            "required_years": 3,
            "candidate_years": 1,
            "meets_requirement": False,
        },
    }

    result = generate_tailoring_plan(
        {},
        ats_result,
        {},
        {},
    )

    priorities = (
        result["tailoring_plan"]["priorities"]
    )

    assert len(priorities) > 0

    for priority in priorities:
        assert "rank" in priority
        assert "area" in priority
        assert "action" in priority


def test_includes_safety_warnings():
    result = generate_tailoring_plan(
        {},
        {},
        {},
        {},
    )

    warnings = (
        result["tailoring_plan"]["warnings"]
    )

    assert len(warnings) > 0

    warning_text = " ".join(
        warnings
    ).lower()

    assert "accurately" in warning_text
    assert "fabricat" in warning_text


def test_does_not_invent_missing_skill_experience():
    ats_result = {
        "missing_skills": ["LLMOps"],
        "missing_qualifications": [],
        "missing_keywords": [],
        "experience": {},
    }

    result = generate_tailoring_plan(
        {},
        ats_result,
        {},
        {},
    )

    skills = result["tailoring_plan"]["skills"]

    assert len(skills) == 1

    recommendation = (
        skills[0]["recommendation"].lower()
    )

    assert "if applicable" in recommendation
    assert "worked with llmops" not in recommendation


def test_does_not_invent_missing_qualification():
    ats_result = {
        "missing_skills": [],
        "missing_qualifications": [
            "Master's degree"
        ],
        "missing_keywords": [],
        "experience": {},
    }

    result = generate_tailoring_plan(
        {},
        ats_result,
        {},
        {},
    )

    qualifications = (
        result["tailoring_plan"]["qualifications"]
    )

    recommendation = (
        qualifications[0]["recommendation"].lower()
    )

    assert "if applicable" in recommendation
    assert "you have a master's degree" not in recommendation


def test_avoids_duplicate_skill_tailoring():
    ats_result = {
        "missing_skills": [
            "MLOps",
            "MLOps",
        ],
        "missing_qualifications": [],
        "missing_keywords": [],
        "experience": {},
    }

    result = generate_tailoring_plan(
        {},
        ats_result,
        {},
        {},
    )

    skills = result["tailoring_plan"]["skills"]

    assert len(skills) == 1


def test_avoids_duplicate_keyword_tailoring():
    ats_result = {
        "missing_skills": [],
        "missing_qualifications": [],
        "missing_keywords": [
            "model validation",
            "model validation",
        ],
        "experience": {},
    }

    result = generate_tailoring_plan(
        {},
        ats_result,
        {},
        {},
    )

    keywords = result["tailoring_plan"]["keywords"]

    assert len(keywords) == 1


def test_uses_existing_improvement_suggestions():
    improvement_suggestions = [
        {
            "type": "experience",
            "priority": "high",
            "current_text": (
                "Worked on machine learning models."
            ),
            "suggestion": (
                "Replace the generic opening with a "
                "specific action verb."
            ),
            "reason": (
                "The current statement does not clearly "
                "communicate your contribution."
            ),
        }
    ]

    result = generate_tailoring_plan(
        {},
        {},
        {},
        {},
        improvement_suggestions,
    )

    experience = (
        result["tailoring_plan"]["experience"]
    )

    assert len(experience) == 1

    suggestion = experience[0]

    assert suggestion["type"] == "experience"
    assert suggestion["action"] == "strengthen"
    assert (
        suggestion["current_text"]
        == "Worked on machine learning models."
    )


def test_does_not_duplicate_existing_improvement_suggestion():
    improvement_suggestions = [
        {
            "type": "skill",
            "priority": "medium",
            "current_text": "",
            "suggestion": (
                "Highlight relevant MLOps experience "
                "in your resume if applicable."
            ),
            "reason": (
                "MLOps is relevant to the job."
            ),
        }
    ]

    ats_result = {
        "missing_skills": ["MLOps"],
        "missing_qualifications": [],
        "missing_keywords": [],
        "experience": {},
    }

    result = generate_tailoring_plan(
        {},
        ats_result,
        {},
        {},
        improvement_suggestions,
    )

    skills = result["tailoring_plan"]["skills"]

    assert len(skills) == 1


def test_preserves_existing_improvement_text():
    current_text = (
        "Worked on data pipelines using Python."
    )

    improvement_suggestions = [
        {
            "type": "experience",
            "priority": "high",
            "current_text": current_text,
            "suggestion": (
                "Replace the generic opening with a "
                "specific action verb."
            ),
            "reason": (
                "The current statement is generic."
            ),
        }
    ]

    result = generate_tailoring_plan(
        {},
        {},
        {},
        {},
        improvement_suggestions,
    )

    experience = (
        result["tailoring_plan"]["experience"]
    )

    assert experience[0]["current_text"] == current_text