from app.resume_content_quality import analyze_resume_content_quality


def complete_resume():
    return {
        "raw_text": """
        Sai Chandra
        sai@example.com
        +91 9876543210

        SKILLS
        Python
        SQL
        Machine Learning

        EDUCATION
        Bachelor of Technology in Computer Science

        WORK EXPERIENCE
        Data Analyst
        ABC Technologies
        2021 - Present

        Developed automated reporting pipelines.
        Improved reporting efficiency by 30%.
        Reduced processing time by 40%.

        PROJECTS
        AI Resume Analyzer
        Built an AI-powered resume analysis application.

        CERTIFICATIONS
        AWS Certified Cloud Practitioner
        """,
        "personal_info": {
            "name": "Sai Chandra",
            "email": "sai@example.com",
            "phone": "+91 9876543210",
        },
        "skills": [
            "Python",
            "SQL",
            "Machine Learning",
        ],
        "education": {
            "section": [
                "Bachelor of Technology in Computer Science",
            ],
            "degrees": [
                "Bachelor of Technology in Computer Science",
            ],
            "years": [],
        },
        "experience": {
            "section": [
                "Data Analyst",
                "ABC Technologies",
                "2021 - Present",
                "Developed automated reporting pipelines.",
                "Improved reporting efficiency by 30%.",
                "Reduced processing time by 40%.",
            ],
            "job_titles": [
                "Data Analyst",
            ],
            "years": [
                "2021 - Present",
            ],
        },
        "projects": [
            "AI Resume Analyzer",
            "Built an AI-powered resume analysis application.",
        ],
        "certifications": [
            "AWS Certified Cloud Practitioner",
        ],
    }


def test_analyzes_complete_resume_content():
    result = analyze_resume_content_quality(
        complete_resume()
    )

    assert "score" in result
    assert 0 <= result["score"] <= 100

    assert "signals" in result
    assert "warnings" in result
    assert "recommendations" in result


def test_detects_contact_information():
    result = analyze_resume_content_quality(
        complete_resume()
    )

    assert result["signals"]["contact_information"] is True


def test_detects_quantified_achievements():
    result = analyze_resume_content_quality(
        complete_resume()
    )

    assert result["signals"]["quantified_achievements"] is True


def test_detects_action_oriented_experience():
    result = analyze_resume_content_quality(
        complete_resume()
    )

    assert result["signals"]["action_oriented_experience"] is True


def test_detects_project_description():
    result = analyze_resume_content_quality(
        complete_resume()
    )

    assert result["signals"]["project_description"] is True


def test_detects_missing_contact_information():
    resume = complete_resume()

    resume["personal_info"]["email"] = None
    resume["personal_info"]["phone"] = None

    result = analyze_resume_content_quality(resume)

    assert result["signals"]["contact_information"] is False
    assert "contact information" in " ".join(
        result["warnings"]
    ).lower()


def test_detects_missing_quantified_achievements():
    resume = complete_resume()

    resume["experience"]["section"] = [
        "Data Analyst",
        "ABC Technologies",
        "2021 - Present",
        "Developed reporting pipelines.",
        "Created dashboards.",
    ]

    result = analyze_resume_content_quality(resume)

    assert result["signals"]["quantified_achievements"] is False


def test_detects_missing_project_description():
    resume = complete_resume()

    resume["projects"] = [
        "AI Resume Analyzer"
    ]

    result = analyze_resume_content_quality(resume)

    assert result["signals"]["project_description"] is False


def test_generates_recommendation_for_missing_signal():
    resume = complete_resume()

    resume["projects"] = [
        "AI Resume Analyzer"
    ]

    result = analyze_resume_content_quality(resume)

    recommendations = " ".join(
        result["recommendations"]
    ).lower()

    assert "project" in recommendations


def test_handles_empty_resume():
    result = analyze_resume_content_quality({})

    assert result["score"] == 0
    assert result["signals"] == {}
    assert result["warnings"] == []
    assert result["recommendations"] == []


def test_handles_none_resume():
    result = analyze_resume_content_quality(None)

    assert result["score"] == 0
    assert result["signals"] == {}
    assert result["warnings"] == []
    assert result["recommendations"] == []

def test_detects_numeric_achievement_without_percentage():
    resume = complete_resume()

    resume["experience"]["section"] = [
        "Data Analyst",
        "ABC Technologies",
        "2021 - Present",
        "Reduced processing time by 15 minutes per report.",
    ]

    result = analyze_resume_content_quality(resume)

    assert result["signals"]["quantified_achievements"] is True


def test_detects_multiplier_achievement():
    resume = complete_resume()

    resume["experience"]["section"] = [
        "Data Analyst",
        "ABC Technologies",
        "2021 - Present",
        "Improved reporting throughput by 2x.",
    ]

    result = analyze_resume_content_quality(resume)

    assert result["signals"]["quantified_achievements"] is True


def test_detects_common_action_verb_variations():
    resume = complete_resume()

    resume["experience"]["section"] = [
        "Data Analyst",
        "ABC Technologies",
        "2021 - Present",
        "Spearheaded automation of reporting workflows.",
        "Streamlined data processing pipelines.",
        "Delivered dashboards for business teams.",
    ]

    result = analyze_resume_content_quality(resume)

    assert result["signals"]["action_oriented_experience"] is True