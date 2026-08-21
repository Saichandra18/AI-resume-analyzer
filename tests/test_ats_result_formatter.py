from app.ats_result_formatter import format_ats_result


def sample_ats_result():
    return {
        "ats_score": 76,
        "skills": {
            "matched": ["Python", "SQL", "Pandas"],
            "missing": ["Power BI", "Machine Learning"],
        },
        "experience": {
            "required_years": 3,
            "candidate_years": 4,
            "meets_requirement": True,
        },
        "qualifications": {
            "matched": ["Bachelor's degree"],
            "missing": [],
        },
        "keywords": {
            "matched": ["data", "analyst"],
            "missing": ["machine learning"],
        },
        "component_scores": {
            "skills": 60.0,
            "experience": 100.0,
            "qualifications": 100.0,
            "keywords": 70.0,
        },
        "weights": {
            "skills": 50.0,
            "experience": 20.0,
            "qualifications": 15.0,
            "keywords": 15.0,
        },
    }


def test_formats_complete_ats_result():
    result = format_ats_result(sample_ats_result())

    expected_keys = {
        "ats_score",
        "matched_skills",
        "missing_skills",
        "experience",
        "matched_qualifications",
        "missing_qualifications",
        "matched_keywords",
        "missing_keywords",
        "component_scores",
        "weights",
    }

    assert set(result.keys()) == expected_keys


def test_formats_matched_and_missing_skills():
    result = format_ats_result(sample_ats_result())

    assert result["matched_skills"] == [
        "Python",
        "SQL",
        "Pandas",
    ]

    assert result["missing_skills"] == [
        "Power BI",
        "Machine Learning",
    ]


def test_formats_experience_result():
    result = format_ats_result(sample_ats_result())

    assert result["experience"] == {
        "required_years": 3,
        "candidate_years": 4,
        "meets_requirement": True,
    }


def test_formats_qualifications():
    result = format_ats_result(sample_ats_result())

    assert result["matched_qualifications"] == [
        "Bachelor's degree"
    ]

    assert result["missing_qualifications"] == []


def test_formats_keywords():
    result = format_ats_result(sample_ats_result())

    assert result["matched_keywords"] == [
        "data",
        "analyst",
    ]

    assert result["missing_keywords"] == [
        "machine learning"
    ]


def test_preserves_ats_score():
    result = format_ats_result(sample_ats_result())

    assert result["ats_score"] == 76


def test_preserves_component_scores():
    result = format_ats_result(sample_ats_result())

    assert result["component_scores"] == {
        "skills": 60.0,
        "experience": 100.0,
        "qualifications": 100.0,
        "keywords": 70.0,
    }


def test_preserves_weights():
    result = format_ats_result(sample_ats_result())

    assert result["weights"] == {
        "skills": 50.0,
        "experience": 20.0,
        "qualifications": 15.0,
        "keywords": 15.0,
    }


def test_handles_empty_matcher_results():
    ats_result = {
        "ats_score": 50,
        "skills": {},
        "experience": {},
        "qualifications": {},
        "keywords": {},
        "component_scores": {},
        "weights": {},
    }

    result = format_ats_result(ats_result)

    assert result["matched_skills"] == []
    assert result["missing_skills"] == []
    assert result["matched_qualifications"] == []
    assert result["missing_qualifications"] == []
    assert result["matched_keywords"] == []
    assert result["missing_keywords"] == []


def test_handles_none_ats_result():
    result = format_ats_result(None)

    assert result["ats_score"] == 0
    assert result["matched_skills"] == []
    assert result["missing_skills"] == []
    assert result["matched_qualifications"] == []
    assert result["missing_qualifications"] == []
    assert result["matched_keywords"] == []
    assert result["missing_keywords"] == []
    assert result["component_scores"] == {}
    assert result["weights"] == {}