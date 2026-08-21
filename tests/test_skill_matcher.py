from app.skill_matcher import match_skills


def test_basic_skill_matching():
    resume_skills = ["Python", "SQL", "Pandas"]
    required_skills = ["Python", "SQL", "Power BI"]

    result = match_skills(resume_skills, required_skills)

    assert result["matched"] == ["Python", "SQL"]
    assert result["missing"] == ["Power BI"]


def test_case_insensitive_matching():
    resume_skills = ["python", "sql"]
    required_skills = ["Python", "SQL"]

    result = match_skills(resume_skills, required_skills)

    assert result["matched"] == ["Python", "SQL"]
    assert result["missing"] == []


def test_whitespace_normalization():
    resume_skills = [" Python ", " SQL "]
    required_skills = ["Python", "SQL"]

    result = match_skills(resume_skills, required_skills)

    assert result["matched"] == ["Python", "SQL"]
    assert result["missing"] == []


def test_duplicate_resume_skills():
    resume_skills = ["Python", "Python", "SQL"]
    required_skills = ["Python", "SQL"]

    result = match_skills(resume_skills, required_skills)

    assert result["matched"] == ["Python", "SQL"]
    assert result["missing"] == []


def test_empty_resume_skills():
    resume_skills = []
    required_skills = ["Python", "SQL"]

    result = match_skills(resume_skills, required_skills)

    assert result["matched"] == []
    assert result["missing"] == ["Python", "SQL"]


def test_empty_required_skills():
    resume_skills = ["Python", "SQL"]
    required_skills = []

    result = match_skills(resume_skills, required_skills)

    assert result["matched"] == []
    assert result["missing"] == []


def test_no_matching_skills():
    resume_skills = ["Java", "C++"]
    required_skills = ["Python", "SQL"]

    result = match_skills(resume_skills, required_skills)

    assert result["matched"] == []
    assert result["missing"] == ["Python", "SQL"]


def test_none_inputs():
    result = match_skills(None, None)

    assert result["matched"] == []
    assert result["missing"] == []