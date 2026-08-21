from app.job_description_processor import clean_job_description


def test_empty_job_description():
    assert clean_job_description("") == ""


def test_none_job_description():
    assert clean_job_description(None) == ""


def test_removes_extra_spaces():
    text = "Python    SQL     Power BI"
    result = clean_job_description(text)

    assert result == "Python SQL Power BI"


def test_removes_spaces_before_punctuation():
    text = "Python , SQL . Power BI :"
    result = clean_job_description(text)

    assert result == "Python, SQL. Power BI:"


def test_normalizes_excessive_blank_lines():
    text = "Python\n\n\n\nSQL"
    result = clean_job_description(text)

    assert result == "Python\n\nSQL"


def test_removes_spaces_around_newlines():
    text = "Python   \n   SQL"
    result = clean_job_description(text)

    assert result == "Python\nSQL"


def test_preserves_job_description_content():
    text = """
    We are looking for a Data Analyst.
    The candidate should have Python, SQL, and Power BI skills.
    """

    result = clean_job_description(text)

    assert "Data Analyst" in result
    assert "Python" in result
    assert "SQL" in result
    assert "Power BI" in result