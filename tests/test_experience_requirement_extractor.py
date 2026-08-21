from app.experience_requirement_extractor import (
    extract_experience_requirement,
)


def test_empty_job_description():
    assert extract_experience_requirement("") is None


def test_none_job_description():
    assert extract_experience_requirement(None) is None


def test_extract_years_of_experience():
    jd = "We need a Data Analyst with 3 years of experience."

    result = extract_experience_requirement(jd)

    assert result["min_years"] == 3
    assert result["text"] == "3 years of experience"


def test_extract_plus_years_of_experience():
    jd = "The candidate should have 5+ years of experience."

    result = extract_experience_requirement(jd)

    assert result["min_years"] == 5
    assert result["text"] == "5+ years of experience"


def test_extract_at_least_experience():
    jd = "The candidate should have at least 4 years of experience."

    result = extract_experience_requirement(jd)

    assert result["min_years"] == 4
    assert result["text"] == "at least 4 years of experience"


def test_extract_minimum_experience():
    jd = "Candidates need minimum of 2 years of experience."

    result = extract_experience_requirement(jd)

    assert result["min_years"] == 2
    assert result["text"] == "minimum of 2 years of experience"


def test_no_experience_requirement():
    jd = "Python, SQL and Power BI skills are required."

    assert extract_experience_requirement(jd) is None


def test_case_insensitive_matching():
    jd = "The candidate needs 3 YEARS OF EXPERIENCE."

    result = extract_experience_requirement(jd)

    assert result["min_years"] == 3