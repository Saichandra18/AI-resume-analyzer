from app.qualification_extractor import extract_required_qualifications


def test_empty_job_description():
    assert extract_required_qualifications("") == []


def test_none_job_description():
    assert extract_required_qualifications(None) == []


def test_bachelors_degree():
    jd = "Bachelor's degree in Computer Science is required."

    result = extract_required_qualifications(jd)

    assert "Bachelor's degree" in result


def test_masters_and_phd():
    jd = "Master's degree or Ph.D. in Computer Science is preferred."

    result = extract_required_qualifications(jd)

    assert "Master's degree" in result
    assert "Ph.D." in result


def test_common_degree_abbreviations():
    jd = "B.Tech or B.E. in Computer Science required. MBA is a plus."

    result = extract_required_qualifications(jd)

    assert "B.Tech" in result
    assert "B.E." in result
    assert "MBA" in result


def test_case_insensitive_matching():
    jd = "bachelor's degree or mca is required."

    result = extract_required_qualifications(jd)

    assert "bachelor's degree" in result
    assert "mca" in result


def test_duplicate_qualifications_are_removed():
    jd = """
    Bachelor's degree required.
    Bachelor's degree in Computer Science preferred.
    """

    result = extract_required_qualifications(jd)

    assert result.count("Bachelor's degree") == 1