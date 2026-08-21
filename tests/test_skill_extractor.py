from app.skill_extractor import extract_skills


def test_extract_python_and_sql():
    text = "I have experience with Python and SQL."

    skills = extract_skills(text)

    assert "Python" in skills
    assert "SQL" in skills


def test_extract_data_analysis_skills():
    text = "Experienced with Pandas, NumPy, and Power BI."

    skills = extract_skills(text)

    assert "Pandas" in skills
    assert "NumPy" in skills
    assert "Power BI" in skills


def test_skill_matching_is_case_insensitive():
    text = "I have experience with PYTHON and pandas."

    skills = extract_skills(text)

    assert "Python" in skills
    assert "Pandas" in skills


def test_no_skills_returns_empty_list():
    text = "I enjoy working with people and solving problems."

    skills = extract_skills(text)

    assert skills == []


def test_empty_text_returns_empty_list():
    skills = extract_skills("")

    assert skills == []