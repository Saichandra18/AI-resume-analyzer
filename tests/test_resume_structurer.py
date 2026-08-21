from app.resume_structurer import structure_resume


def test_structure_complete_resume():
    text = """Sai Chandra
sai@example.com
+91 9876543210

SKILLS

Python
SQL
Power BI

EDUCATION

Bachelor of Technology in Computer Science
ABC University
2020 - 2024

WORK EXPERIENCE

Data Analyst
ABC Technologies
2024 - Present

Created Power BI dashboards.

PROJECTS

AI Resume Analyzer
Built an AI-powered resume analysis application.

CERTIFICATIONS

AWS Certified Cloud Practitioner
"""

    resume = structure_resume(text)

    assert resume["personal_info"]["name"] == "Sai Chandra"
    assert resume["personal_info"]["email"] == "sai@example.com"
    assert resume["personal_info"]["phone"] == "+91 9876543210"

    assert "Python" in resume["skills"]
    assert "SQL" in resume["skills"]
    assert "Power BI" in resume["skills"]

    assert "Bachelor of Technology in Computer Science" in resume["education"]["degrees"]

    assert "Data Analyst" in resume["experience"]["job_titles"]

    assert "AI Resume Analyzer" in resume["projects"]

    assert "AWS Certified Cloud Practitioner" in resume["certifications"]


def test_structure_empty_resume():
    resume = structure_resume("")

    assert resume["personal_info"]["name"] is None
    assert resume["personal_info"]["email"] is None
    assert resume["personal_info"]["phone"] is None

    assert resume["skills"] == []
    assert resume["education"]["section"] == []
    assert resume["experience"]["section"] == []
    assert resume["projects"] == []
    assert resume["certifications"] == []


def test_structure_resume_without_optional_sections():
    text = """Sai Chandra
sai@example.com
+91 9876543210

SKILLS

Python
SQL
"""

    resume = structure_resume(text)

    assert resume["personal_info"]["name"] == "Sai Chandra"
    assert resume["personal_info"]["email"] == "sai@example.com"
    assert resume["personal_info"]["phone"] == "+91 9876543210"

    assert "Python" in resume["skills"]
    assert "SQL" in resume["skills"]

    assert resume["education"]["section"] == []
    assert resume["experience"]["section"] == []
    assert resume["projects"] == []
    assert resume["certifications"] == []