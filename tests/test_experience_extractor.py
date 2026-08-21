from app.experience_extractor import (
    find_experience_section,
    extract_job_titles,
    extract_experience_years,
)


def test_find_experience_section():
    text = """WORK EXPERIENCE

Data Analyst
ABC Technologies
2023 - Present

Created Power BI dashboards.

EDUCATION

Bachelor of Technology"""

    experience = find_experience_section(text)

    assert "Data Analyst" in experience
    assert "ABC Technologies" in experience
    assert "2023 - Present" in experience
    assert "Bachelor of Technology" not in experience


def test_find_experience_section_when_missing():
    text = """EDUCATION

Bachelor of Technology

SKILLS

Python
SQL"""

    experience = find_experience_section(text)

    assert experience == []


def test_extract_job_titles():
    text = """Data Analyst
Software Engineer
Project Manager
ABC Technologies"""

    job_titles = extract_job_titles(text)

    assert "Data Analyst" in job_titles
    assert "Software Engineer" in job_titles
    assert "Project Manager" in job_titles


def test_extract_experience_years():
    text = """Data Analyst
ABC Technologies
2023 - Present

Software Developer
XYZ Company
2020 - 2023"""

    years = extract_experience_years(text)

    assert "2023 - Present" in years
    assert "2020 - 2023" in years


def test_empty_text():
    assert find_experience_section("") == []
    assert extract_job_titles("") == []
    assert extract_experience_years("") == []