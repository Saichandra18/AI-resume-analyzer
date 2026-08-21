from app.job_description_analyzer import analyze_job_description


def test_empty_job_description():
    result = analyze_job_description("")

    assert result == {
        "cleaned_text": "",
        "required_skills": [],
        "qualifications": [],
        "experience": None,
        "keywords": [],
    }


def test_none_job_description():
    result = analyze_job_description(None)

    assert result == {
        "cleaned_text": "",
        "required_skills": [],
        "qualifications": [],
        "experience": None,
        "keywords": [],
    }


def test_complete_job_description_analysis():
    jd = """
    We are looking for a Data Analyst with 3+ years of experience.

    Bachelor's degree in Computer Science is required.

    The candidate should have strong skills in Python, SQL,
    Pandas and Power BI.
    """

    result = analyze_job_description(jd)

    assert "Data Analyst" in result["cleaned_text"]

    assert "Python" in result["required_skills"]
    assert "SQL" in result["required_skills"]
    assert "Pandas" in result["required_skills"]
    assert "Power BI" in result["required_skills"]

    assert "Bachelor's degree" in result["qualifications"]

    assert result["experience"]["min_years"] == 3

    assert "data analyst" in result["keywords"]
    assert "power bi" in result["keywords"]
    assert "python" in result["keywords"]
    assert "sql" in result["keywords"]


def test_job_description_without_experience():
    jd = """
    Data Analyst required.
    Bachelor's degree preferred.
    Strong Python and SQL skills required.
    """

    result = analyze_job_description(jd)

    assert result["experience"] is None
    assert "Python" in result["required_skills"]
    assert "SQL" in result["required_skills"]
    assert "Bachelor's degree" in result["qualifications"]


def test_job_description_without_qualifications():
    jd = """
    Data Analyst with 2+ years of experience.
    Strong Python and SQL skills required.
    """

    result = analyze_job_description(jd)

    assert result["qualifications"] == []
    assert result["experience"]["min_years"] == 2
    assert "Python" in result["required_skills"]
    assert "SQL" in result["required_skills"]


def test_job_description_without_skills():
    jd = """
    Bachelor's degree required.
    Minimum of 3 years of experience.
    """

    result = analyze_job_description(jd)

    assert result["required_skills"] == []
    assert "Bachelor's degree" in result["qualifications"]
    assert result["experience"]["min_years"] == 3