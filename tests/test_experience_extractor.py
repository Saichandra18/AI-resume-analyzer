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


def test_extract_job_titles_only_from_experience_section():
    text = """Education
Bachelor of Technology in Computer Science
Software Engineering Diploma

Experience
Software Engineer
ABC Technologies
2023 - Present

Projects
Machine Learning Engineer Project
"""

    job_titles = extract_job_titles(text)

    assert job_titles == [
        "Software Engineer"
    ]


def test_extract_experience_years_only_from_experience_section():
    text = """Education
Bachelor of Technology
ABC University
2019 - 2023

Experience
Software Engineer
ABC Technologies
2023 - Present
"""

    years = extract_experience_years(text)

    assert years == [
        "2023 - Present"
    ]


def test_experience_section_stops_at_core_competencies():
    text = """Experience
Freelance LLM Trainer
Outlier
2023 - Present
Supported LLM evaluation.

Core Competencies
Programming: Python, SQL
Machine Learning: Supervised Learning
Generative AI: LLMs, RAG
"""

    experience = find_experience_section(text)

    assert "Freelance LLM Trainer" in experience
    assert "Supported LLM evaluation." in experience
    assert "Programming: Python, SQL" not in experience
    assert "Generative AI: LLMs, RAG" not in experience


def test_extract_trainer_job_title():
    text = """Experience
Freelance LLM Trainer - Outlier
Remote, India
2023 - Present

Education
Bachelor of Technology
"""

    job_titles = extract_job_titles(text)

    assert job_titles == [
        "Freelance LLM Trainer - Outlier"
    ]


def test_extract_corrupted_trainer_job_title():
    text = """Experience
F reelance LLM T rainer – OutlierSep 2023 – Present
Remote, India
•Contributed to training and evaluation of Large Language Models.

Education
Bachelor of Technology
2019 - 2023
"""

    job_titles = extract_job_titles(text)

    assert job_titles == [
        "Freelance LLM Trainer – OutlierSep 2023 – Present"
    ]