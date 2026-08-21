from app.name_extractor import extract_name


def test_extract_name_from_first_line():
    text = """Sai Chandra
Data Analyst
sai@example.com
+91 9876543210"""

    name = extract_name(text)

    assert name == "Sai Chandra"


def test_extract_name_after_resume_heading():
    text = """RESUME

Sai Chandra
Data Analyst
sai@example.com"""

    name = extract_name(text)

    assert name == "Sai Chandra"


def test_ignore_email_and_phone():
    text = """9876543210
sai@example.com
Sai Chandra
Data Analyst"""

    name = extract_name(text)

    assert name == "Sai Chandra"


def test_no_name_returns_none():
    text = """RESUME
Data Analyst
Python SQL Power BI
Experience"""

    name = extract_name(text)

    assert name is None


def test_empty_text_returns_none():
    name = extract_name("")

    assert name is None