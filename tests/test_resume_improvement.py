from app.resume_improvement import generate_improvement_suggestions


def test_returns_empty_for_empty_resume():
    result = generate_improvement_suggestions(
        {},
        {},
        {},
    )

    assert result == {
        "improvement_suggestions": []
    }


def test_returns_empty_for_none_resume():
    result = generate_improvement_suggestions(
        None,
        {},
        {},
    )

    assert result == {
        "improvement_suggestions": []
    }


def test_detects_weak_experience_statement():
    resume_data = {
        "experience": {
            "section": [
                "Worked on machine learning models."
            ]
        }
    }

    result = generate_improvement_suggestions(
        resume_data,
        {},
        {},
    )

    suggestions = result["improvement_suggestions"]

    assert len(suggestions) == 1

    suggestion = suggestions[0]

    assert suggestion["type"] == "experience"
    assert suggestion["priority"] == "high"
    assert (
        suggestion["current_text"]
        == "Worked on machine learning models."
    )
    assert "action" in suggestion["suggestion"].lower()
    assert "contribution" in suggestion["reason"].lower()


def test_detects_responsible_for_statement():
    resume_data = {
        "experience": {
            "section": [
                "Responsible for data analysis and reporting."
            ]
        }
    }

    result = generate_improvement_suggestions(
        resume_data,
        {},
        {},
    )

    suggestions = result["improvement_suggestions"]

    assert len(suggestions) == 1

    suggestion = suggestions[0]

    assert suggestion["type"] == "experience"
    assert suggestion["priority"] == "high"
    assert (
        suggestion["current_text"]
        == "Responsible for data analysis and reporting."
    )


def test_does_not_flag_strong_experience_statement():
    resume_data = {
        "experience": {
            "section": [
                "Developed machine learning models for predictive analysis."
            ]
        }
    }

    result = generate_improvement_suggestions(
        resume_data,
        {},
        {},
    )

    assert result["improvement_suggestions"] == []


def test_suggests_quantification_when_missing():
    resume_data = {
        "experience": {
            "section": [
                "Developed machine learning models."
            ]
        }
    }

    content_quality = {
        "signals": {
            "quantified_achievements": False
        }
    }

    result = generate_improvement_suggestions(
        resume_data,
        {},
        content_quality,
    )

    suggestions = result["improvement_suggestions"]

    types = [
        suggestion["type"]
        for suggestion in suggestions
    ]

    assert "achievement" in types

    achievement = next(
        suggestion
        for suggestion in suggestions
        if suggestion["type"] == "achievement"
    )

    assert achievement["priority"] == "high"
    assert "measurable" in achievement["suggestion"].lower()
    assert "invent" not in achievement["suggestion"].lower()


def test_suggests_project_improvement():
    resume_data = {
        "projects": [
            "Resume Analyzer"
        ]
    }

    content_quality = {
        "signals": {
            "project_description": False
        }
    }

    result = generate_improvement_suggestions(
        resume_data,
        {},
        content_quality,
    )

    suggestions = result["improvement_suggestions"]

    project_suggestions = [
        suggestion
        for suggestion in suggestions
        if suggestion["type"] == "project"
    ]

    assert len(project_suggestions) == 1

    suggestion = project_suggestions[0]

    assert suggestion["priority"] == "medium"
    assert "technologies" in suggestion["suggestion"].lower()
    assert "contribution" in suggestion["suggestion"].lower()


def test_suggests_missing_resume_section():
    resume_data = {}

    resume_quality = {
        "missing_sections": [
            "projects"
        ]
    }

    result = generate_improvement_suggestions(
        resume_data,
        resume_quality,
        {},
    )

    suggestions = result["improvement_suggestions"]

    assert len(suggestions) == 1

    suggestion = suggestions[0]

    assert suggestion["type"] == "section"
    assert suggestion["priority"] == "medium"
    assert suggestion["current_text"] == ""
    assert "projects" in suggestion["suggestion"].lower()


def test_preserves_current_experience_text():
    current_text = (
        "Worked on data pipelines using Python."
    )

    resume_data = {
        "experience": {
            "section": [current_text]
        }
    }

    result = generate_improvement_suggestions(
        resume_data,
        {},
        {},
    )

    suggestion = result["improvement_suggestions"][0]

    assert suggestion["current_text"] == current_text


def test_does_not_invent_metrics():
    resume_data = {
        "experience": {
            "section": [
                "Developed machine learning models."
            ]
        }
    }

    content_quality = {
        "signals": {
            "quantified_achievements": False
        }
    }

    result = generate_improvement_suggestions(
        resume_data,
        {},
        content_quality,
    )

    achievement = next(
        suggestion
        for suggestion in result["improvement_suggestions"]
        if suggestion["type"] == "achievement"
    )

    suggestion_text = (
        achievement["suggestion"].lower()
    )

    assert "18%" not in suggestion_text
    assert "20%" not in suggestion_text
    assert "50%" not in suggestion_text
    assert "100%" not in suggestion_text


def test_avoids_duplicate_suggestions():
    resume_data = {
        "experience": {
            "section": [
                "Worked on machine learning models.",
                "Worked on machine learning models.",
            ]
        }
    }

    result = generate_improvement_suggestions(
        resume_data,
        {},
        {},
    )

    experience_suggestions = [
        suggestion
        for suggestion in result["improvement_suggestions"]
        if suggestion["type"] == "experience"
    ]

    assert len(experience_suggestions) == 1

def test_suggests_missing_skill_improvement():
    resume_data = {
        "experience": {
            "section": [
                "Developed machine learning models."
            ]
        }
    }

    ats_result = {
        "missing_skills": ["MLOps"],
        "missing_qualifications": [],
        "missing_keywords": [],
    }

    result = generate_improvement_suggestions(
        resume_data,
        {},
        {},
        ats_result,
    )

    suggestions = result["improvement_suggestions"]

    skill_suggestions = [
        suggestion
        for suggestion in suggestions
        if suggestion["type"] == "skill"
    ]

    assert len(skill_suggestions) == 1

    suggestion = skill_suggestions[0]

    assert suggestion["priority"] == "medium"
    assert suggestion["current_text"] == ""
    assert "MLOps" in suggestion["suggestion"]
    assert "applicable" in suggestion["suggestion"].lower()
    assert "job" in suggestion["reason"].lower()


def test_suggests_missing_keyword_improvement():
    resume_data = {
        "experience": {
            "section": [
                "Developed machine learning models."
            ]
        }
    }

    ats_result = {
        "missing_skills": [],
        "missing_qualifications": [],
        "missing_keywords": ["model validation"],
    }

    result = generate_improvement_suggestions(
        resume_data,
        {},
        {},
        ats_result,
    )

    suggestions = result["improvement_suggestions"]

    keyword_suggestions = [
        suggestion
        for suggestion in suggestions
        if suggestion["type"] == "keyword"
    ]

    assert len(keyword_suggestions) == 1

    suggestion = keyword_suggestions[0]

    assert suggestion["priority"] == "medium"
    assert "model validation" in suggestion["suggestion"].lower()
    assert "applicable" in suggestion["suggestion"].lower()


def test_suggests_missing_qualification_improvement():
    resume_data = {
        "education": {
            "degrees": [
                "Bachelor of Technology"
            ]
        }
    }

    ats_result = {
        "missing_skills": [],
        "missing_qualifications": [
            "Master's degree"
        ],
        "missing_keywords": [],
    }

    result = generate_improvement_suggestions(
        resume_data,
        {},
        {},
        ats_result,
    )

    suggestions = result["improvement_suggestions"]

    qualification_suggestions = [
        suggestion
        for suggestion in suggestions
        if suggestion["type"] == "qualification"
    ]

    assert len(qualification_suggestions) == 1

    suggestion = qualification_suggestions[0]

    assert suggestion["priority"] == "medium"
    assert "master's degree" in (
        suggestion["suggestion"].lower()
    )
    assert "applicable" in (
        suggestion["suggestion"].lower()
    )


def test_does_not_invent_missing_skill_experience():
    ats_result = {
        "missing_skills": ["LLMOps"],
        "missing_qualifications": [],
        "missing_keywords": [],
    }

    result = generate_improvement_suggestions(
        {},
        {},
        {},
        ats_result,
    )

    suggestions = result["improvement_suggestions"]

    assert len(suggestions) == 1

    suggestion = suggestions[0]

    assert suggestion["type"] == "skill"
    assert "if applicable" in (
        suggestion["suggestion"].lower()
    )
    assert "worked with llmops" not in (
        suggestion["suggestion"].lower()
    )


def test_generates_multiple_ats_gap_improvements():
    ats_result = {
        "missing_skills": [
            "MLOps",
            "LLMOps",
        ],
        "missing_qualifications": [],
        "missing_keywords": [
            "model validation",
        ],
    }

    result = generate_improvement_suggestions(
        {},
        {},
        {},
        ats_result,
    )

    suggestions = result["improvement_suggestions"]

    assert len(suggestions) == 3

    assert suggestions[0]["type"] == "skill"
    assert suggestions[1]["type"] == "skill"
    assert suggestions[2]["type"] == "keyword"