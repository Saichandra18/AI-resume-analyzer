from app.job_skill_extractor import extract_required_skills


def test_empty_job_description():
    assert extract_required_skills("") == []


def test_none_job_description():
    assert extract_required_skills(None) == []


def test_extract_common_skills():
    jd = "We need a Data Analyst with Python, SQL and Pandas experience."

    result = extract_required_skills(jd)

    assert "Python" in result
    assert "SQL" in result
    assert "Pandas" in result


def test_skill_matching_is_case_insensitive():
    jd = "Experience with PYTHON, sql and power bi is required."

    result = extract_required_skills(jd)

    assert result == ["Python", "SQL", "Power BI"]


def test_multi_word_skills():
    jd = "Experience with Machine Learning and Natural Language Processing."

    result = extract_required_skills(jd)

    assert "Machine Learning" in result
    assert "Natural Language Processing" in result


def test_special_character_skills():
    jd = "Experience with C++, C#, Node.js and Scikit-learn."

    result = extract_required_skills(jd)

    assert "C++" in result
    assert "C#" in result
    assert "Node.js" in result
    assert "Scikit-learn" in result


def test_does_not_match_partial_skill_names():
    jd = "The candidate should know Pythonic programming."

    result = extract_required_skills(jd)

    assert "Python" not in result


def test_returns_dictionary_spelling():
    jd = "The candidate should know python and POWER BI."

    result = extract_required_skills(jd)

    assert "Python" in result
    assert "Power BI" in result