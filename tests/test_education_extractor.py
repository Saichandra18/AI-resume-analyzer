from app.education_extractor import (
    find_education_section,
    extract_degrees,
    extract_education_years,
)


def test_find_education_section():
    text = """Education

Bachelor of Technology in Computer Science
ABC University
2020 - 2024

Experience

Data Analyst
XYZ Company"""

    education = find_education_section(text)

    assert "Bachelor of Technology in Computer Science" in education
    assert "ABC University" in education
    assert "2020 - 2024" in education
    assert "Data Analyst" not in education


def test_find_education_section_when_missing():
    text = """Skills
Python
SQL
Power BI"""

    education = find_education_section(text)

    assert education == []


def test_extract_degrees():
    text = """Bachelor of Technology in Computer Science
Master of Business Administration
ABC University"""

    degrees = extract_degrees(text)

    assert "Bachelor of Technology in Computer Science" in degrees
    assert "Master of Business Administration" in degrees


def test_extract_education_years():
    text = """Bachelor of Technology
ABC University
2020 - 2024"""

    years = extract_education_years(text)

    assert "2020" in years
    assert "2024" in years


def test_empty_text():
    assert find_education_section("") == []
    assert extract_degrees("") == []
    assert extract_education_years("") == []