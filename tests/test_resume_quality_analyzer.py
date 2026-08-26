from app.resume_quality_analyzer import analyze_resume_quality


def complete_resume():
    return {
        "personal_info": {
            "name": "Sai Chandra",
            "email": "sai@example.com",
            "phone": "+91 9876543210",
        },
        "skills": [
            "Python",
            "SQL",
        ],
        "education": {
            "section": [
                "Bachelor of Technology in Computer Science",
            ],
            "degrees": [
                "Bachelor of Technology in Computer Science",
            ],
            "years": [
                "2020",
                "2024",
            ],
        },
        "experience": {
            "section": [
                "Data Analyst",
                "ABC Technologies",
                "2024 - Present",
            ],
            "job_titles": [
                "Data Analyst",
            ],
            "years": [
                "2024 - Present",
            ],
        },
        "projects": [
            "AI Resume Analyzer",
        ],
        "certifications": [
            "AWS Certified Cloud Practitioner",
        ],
    }


def test_complete_resume_has_full_score():
    result = analyze_resume_quality(
        complete_resume()
    )

    assert result["score"] == 100
    assert result["missing_sections"] == []


def test_name_is_required():
    resume = complete_resume()

    resume["personal_info"]["name"] = None

    result = analyze_resume_quality(resume)

    assert "name" in result["missing_sections"]
    assert result["score"] < 100


def test_email_is_required():
    resume = complete_resume()

    resume["personal_info"]["email"] = None

    result = analyze_resume_quality(resume)

    assert "email" in result["missing_sections"]
    assert result["score"] < 100


def test_phone_is_required():
    resume = complete_resume()

    resume["personal_info"]["phone"] = None

    result = analyze_resume_quality(resume)

    assert "phone" in result["missing_sections"]
    assert result["score"] < 100


def test_skills_are_required():
    resume = complete_resume()

    resume["skills"] = []

    result = analyze_resume_quality(resume)

    assert "skills" in result["missing_sections"]
    assert result["score"] < 100


def test_education_is_required():
    resume = complete_resume()

    resume["education"] = {
        "section": [],
        "degrees": [],
        "years": [],
    }

    result = analyze_resume_quality(resume)

    assert "education" in result["missing_sections"]
    assert result["score"] < 100


def test_experience_is_required():
    resume = complete_resume()

    resume["experience"] = {
        "section": [],
        "job_titles": [],
        "years": [],
    }

    result = analyze_resume_quality(resume)

    assert "experience" in result["missing_sections"]
    assert result["score"] < 100


def test_projects_are_required():
    resume = complete_resume()

    resume["projects"] = []

    result = analyze_resume_quality(resume)

    assert "projects" in result["missing_sections"]
    assert result["score"] < 100


def test_certifications_are_optional():
    resume = complete_resume()

    resume["certifications"] = []

    result = analyze_resume_quality(resume)

    assert result["score"] == 100
    assert "certifications" not in result["missing_sections"]
    assert result["optional_sections"]["certifications"]["present"] is False


def test_empty_resume_returns_zero_score():
    result = analyze_resume_quality({})

    assert result["score"] == 0
    assert set(result["missing_sections"]) == {
        "name",
        "email",
        "phone",
        "skills",
        "education",
        "experience",
        "projects",
    }


def test_none_resume_returns_zero_score():
    result = analyze_resume_quality(None)

    assert result["score"] == 0
    assert set(result["missing_sections"]) == {
        "name",
        "email",
        "phone",
        "skills",
        "education",
        "experience",
        "projects",
    }