from app.job_keyword_extractor import extract_job_keywords


def test_empty_job_description():
    assert extract_job_keywords("") == []


def test_none_job_description():
    assert extract_job_keywords(None) == []


def test_extracts_meaningful_keywords():
    jd = """
    We are looking for a Data Analyst with experience
    in Python, SQL and Power BI.
    """

    result = extract_job_keywords(jd)

    assert "data analyst" in result
    assert "python" in result
    assert "sql" in result
    assert "power bi" in result


def test_generic_words_are_not_keywords():
    jd = """
    The candidate should have experience in working
    with teams to ensure good quality and provide
    support for various projects.
    """

    result = extract_job_keywords(jd)

    assert "candidate" not in result
    assert "working" not in result
    assert "ensure" not in result
    assert "good" not in result
    assert "quality" not in result
    assert "provide" not in result
    assert "support" not in result
    assert "various" not in result
    assert "projects" not in result


def test_stop_words_are_not_keywords():
    jd = """
    The candidate should have experience in Python
    and SQL with the required skills.
    """

    result = extract_job_keywords(jd)

    assert "the" not in result
    assert "in" not in result
    assert "and" not in result
    assert "with" not in result


def test_extracts_multi_word_technical_concepts():
    jd = """
    Experience with Machine Learning, Deep Learning,
    Artificial Intelligence, Retrieval Augmented Generation,
    and Model Evaluation is required.
    """

    result = extract_job_keywords(jd)

    assert "machine learning" in result
    assert "deep learning" in result
    assert "artificial intelligence" in result
    assert "retrieval augmented generation" in result
    assert "model evaluation" in result


def test_multi_word_concepts_are_not_split():
    jd = """
    Experience with Machine Learning and Deep Learning.
    """

    result = extract_job_keywords(jd)

    assert "machine" not in result
    assert "learning" not in result
    assert "deep" not in result


def test_duplicate_keywords_are_removed():
    jd = """
    Python Python Python
    Machine Learning Machine Learning
    """

    result = extract_job_keywords(jd)

    assert result.count("python") == 1
    assert result.count("machine learning") == 1


def test_keywords_are_lowercase():
    jd = """
    PYTHON SQL Machine Learning POWER BI
    """

    result = extract_job_keywords(jd)

    assert "python" in result
    assert "sql" in result
    assert "machine learning" in result
    assert "power bi" in result


def test_locations_and_numbers_are_not_keywords():
    jd = """
    This position is based in Bengaluru.
    Minimum 5 years of experience is required.
    """

    result = extract_job_keywords(jd)

    assert "bengaluru" not in result
    assert "5" not in result
    assert "years" not in result

def test_does_not_extract_partial_retrieval_augmented_phrase():
    jd = """
    Experience with Retrieval Augmented Generation (RAG)
    for building LLM applications.
    """

    result = extract_job_keywords(jd)

    assert "retrieval augmented generation" in result
    assert "retrieval augmented" not in result