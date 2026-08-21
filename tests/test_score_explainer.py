from app.score_explainer import explain_ats_score


def sample_ats_result():
    return {
        "ats_score": 76,
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


def test_explains_complete_ats_score():
    result = explain_ats_score(sample_ats_result())

    assert result["ats_score"] == 76

    assert result["components"]["skills"]["score"] == 60.0
    assert result["components"]["skills"]["weight"] == 50.0

    assert result["components"]["experience"]["score"] == 100.0
    assert result["components"]["experience"]["weight"] == 20.0

    assert result["components"]["qualifications"]["score"] == 100.0
    assert result["components"]["qualifications"]["weight"] == 15.0

    assert result["components"]["keywords"]["score"] == 70.0
    assert result["components"]["keywords"]["weight"] == 15.0


def test_calculates_weighted_component_contributions():
    result = explain_ats_score(sample_ats_result())

    assert result["components"]["skills"]["contribution"] == 30.0
    assert result["components"]["experience"]["contribution"] == 20.0
    assert result["components"]["qualifications"]["contribution"] == 15.0
    assert result["components"]["keywords"]["contribution"] == 10.5


def test_total_contribution_matches_unrounded_score():
    result = explain_ats_score(sample_ats_result())

    assert result["total_contribution"] == 75.5


def test_preserves_final_ats_score():
    result = explain_ats_score(sample_ats_result())

    assert result["ats_score"] == 76


def test_handles_unavailable_component():
    ats_result = {
        "ats_score": 80,
        "component_scores": {
            "skills": 80.0,
            "experience": 100.0,
            "qualifications": None,
            "keywords": 60.0,
        },
        "weights": {
            "skills": 50.0,
            "experience": 20.0,
            "keywords": 30.0,
        },
    }

    result = explain_ats_score(ats_result)

    assert result["components"]["qualifications"]["score"] is None
    assert result["components"]["qualifications"]["weight"] is None
    assert result["components"]["qualifications"]["contribution"] is None


def test_handles_empty_ats_result():
    result = explain_ats_score({})

    assert result["ats_score"] == 0
    assert result["components"] == {}
    assert result["total_contribution"] == 0.0


def test_handles_none_ats_result():
    result = explain_ats_score(None)

    assert result["ats_score"] == 0
    assert result["components"] == {}
    assert result["total_contribution"] == 0.0