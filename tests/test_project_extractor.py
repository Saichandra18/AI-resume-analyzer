from app.project_extractor import find_project_section


def test_find_project_section():
    text = """PROJECTS

AI Resume Analyzer
Python, Flask, NLP
Built an AI-powered resume analysis application.

Cricket Analytics Dashboard
Python, SQL, Power BI
Created an IPL analytics dashboard.

EDUCATION

Bachelor of Technology"""

    projects = find_project_section(text)

    assert "AI Resume Analyzer" in projects
    assert "Cricket Analytics Dashboard" in projects
    assert "Python, Flask, NLP" in projects
    assert "Bachelor of Technology" not in projects


def test_find_project_section_when_missing():
    text = """EXPERIENCE

Data Analyst
ABC Technologies

EDUCATION

Bachelor of Technology"""

    projects = find_project_section(text)

    assert projects == []


def test_project_section_stops_at_skills():
    text = """PROJECTS

AI Resume Analyzer
Built an AI-powered application.

SKILLS

Python
SQL
Power BI"""

    projects = find_project_section(text)

    assert "AI Resume Analyzer" in projects
    assert "Built an AI-powered application." in projects
    assert "Python" not in projects
    assert "SQL" not in projects


def test_personal_projects_heading():
    text = """PERSONAL PROJECTS

Portfolio Website
Built a personal portfolio website.

EDUCATION

Bachelor of Technology"""

    projects = find_project_section(text)

    assert "Portfolio Website" in projects
    assert "Built a personal portfolio website." in projects


def test_empty_text():
    projects = find_project_section("")

    assert projects == []