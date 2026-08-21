from app.certification_extractor import find_certification_section


def test_find_certification_section():
    text = """CERTIFICATIONS

AWS Certified Cloud Practitioner
Google Data Analytics Professional Certificate
Microsoft Power BI Data Analyst

PROJECTS

AI Resume Analyzer"""

    certifications = find_certification_section(text)

    assert "AWS Certified Cloud Practitioner" in certifications
    assert "Google Data Analytics Professional Certificate" in certifications
    assert "Microsoft Power BI Data Analyst" in certifications
    assert "AI Resume Analyzer" not in certifications


def test_find_certification_section_when_missing():
    text = """EXPERIENCE

Data Analyst
ABC Technologies

SKILLS

Python
SQL"""

    certifications = find_certification_section(text)

    assert certifications == []


def test_certification_section_stops_at_education():
    text = """CERTIFICATIONS

AWS Certified Cloud Practitioner
Google Data Analytics Professional Certificate

EDUCATION

Bachelor of Technology"""

    certifications = find_certification_section(text)

    assert "AWS Certified Cloud Practitioner" in certifications
    assert "Google Data Analytics Professional Certificate" in certifications
    assert "Bachelor of Technology" not in certifications


def test_licenses_and_certifications_heading():
    text = """LICENSES & CERTIFICATIONS

AWS Certified Cloud Practitioner
Microsoft Power BI Data Analyst

SKILLS

Python
SQL"""

    certifications = find_certification_section(text)

    assert "AWS Certified Cloud Practitioner" in certifications
    assert "Microsoft Power BI Data Analyst" in certifications
    assert "Python" not in certifications


def test_empty_text():
    certifications = find_certification_section("")

    assert certifications == []