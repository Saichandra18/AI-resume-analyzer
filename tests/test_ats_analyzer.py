from app.ats_analyzer import analyze_resume_against_job


def test_complete_ats_analysis():
    resume_data = {
        "personal_info": {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "1234567890",
        },
        "skills": [
            "Python",
            "SQL",
            "Pandas",
            "Power BI",
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
                "2021 - Present",
            ],
            "job_titles": [
                "Data Analyst",
            ],
            "years": [
                "2021 - Present",
            ],
        },
        "projects": [
            "Sales Dashboard",
        ],
        "certifications": [],
    }

    job_description = """
    We are looking for a Data Analyst with 3+ years of experience.

    Bachelor's degree is required.

    Strong skills in Python, SQL, Pandas and Machine Learning.

    Experience with Power BI dashboards is preferred.
    """

    result = analyze_resume_against_job(
        resume_data,
        job_description,
    )

    assert isinstance(result["ats_score"], int)
    assert 0 <= result["ats_score"] <= 100

    assert "Python" in result["skills"]["matched"]
    assert "SQL" in result["skills"]["matched"]
    assert "Pandas" in result["skills"]["matched"]

    assert "Machine Learning" in result["skills"]["missing"]

    assert result["experience"]["required_years"] == 3
    assert result["experience"]["candidate_years"] >= 3
    assert result["experience"]["meets_requirement"] is True

    assert "Bachelor's degree" in result["qualifications"]["matched"]

    assert "component_scores" in result
    assert "weights" in result


def test_perfect_resume_job_match():

    resume_data = {
        "skills": [
            "Python",
            "SQL",
            "Pandas",
        ],
        "education": {
            "degrees": [
                "Bachelor of Technology in Computer Science",
            ]
        },
        "experience": {
            "section": [
                "Data Analyst",
                "2021 - Present",
            ],
            "job_titles": [
                "Data Analyst",
            ],
            "years": [
                "2021 - Present",
            ],
        },
        "projects": [],
        "certifications": [],
    }

    job_description = """
    Data Analyst with 3+ years of experience.
    Bachelor's degree required.
    Strong Python, SQL and Pandas skills.
    """

    result = analyze_resume_against_job(
        resume_data,
        job_description,
    )

    assert result["skills"]["missing"] == []
    assert result["experience"]["meets_requirement"] is True
    assert result["qualifications"]["missing"] == []

    assert result["ats_score"] >= 90


def test_missing_skills_reduce_score():

    resume_data = {
        "skills": [
            "Python",
        ],
        "education": {
            "degrees": [
                "Bachelor of Technology",
            ]
        },
        "experience": {
            "section": [
                "Data Analyst",
                "2021 - Present",
            ],
            "job_titles": [
                "Data Analyst",
            ],
            "years": [
                "2021 - Present",
            ],
        },
        "projects": [],
        "certifications": [],
    }

    job_description = """
    Data Analyst with 3+ years of experience.
    Bachelor's degree required.
    Strong Python, SQL, Pandas and Power BI skills.
    """

    result = analyze_resume_against_job(
        resume_data,
        job_description,
    )

    assert result["skills"]["matched"] == ["Python"]

    assert "SQL" in result["skills"]["missing"]
    assert "Pandas" in result["skills"]["missing"]
    assert "Power BI" in result["skills"]["missing"]

    assert result["ats_score"] < 90


def test_no_experience_requirement():

    resume_data = {
        "skills": [
            "Python",
        ],
        "education": {
            "degrees": [
                "Bachelor of Technology",
            ]
        },
        "experience": {
            "section": [],
            "job_titles": [],
            "years": [],
        },
        "projects": [],
        "certifications": [],
    }

    job_description = """
    Data Analyst.
    Bachelor's degree required.
    Strong Python skills.
    """

    result = analyze_resume_against_job(
        resume_data,
        job_description,
    )

    assert result["experience"]["required_years"] is None
    assert result["experience"]["meets_requirement"] is True

    assert result["component_scores"]["experience"] is None


def test_empty_job_description():

    resume_data = {
        "skills": ["Python"],
        "education": {
            "degrees": [
                "Bachelor of Technology",
            ]
        },
        "experience": {
            "section": [],
            "job_titles": [],
            "years": [],
        },
        "projects": [],
        "certifications": [],
    }

    result = analyze_resume_against_job(
        resume_data,
        "",
    )

    assert result["ats_score"] == 0

    assert result["skills"]["matched"] == []
    assert result["skills"]["missing"] == []

    assert result["qualifications"]["matched"] == []
    assert result["qualifications"]["missing"] == []

    assert result["keywords"]["matched"] == []
    assert result["keywords"]["missing"] == []