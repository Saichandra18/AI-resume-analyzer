from app.recommendation_engine import generate_recommendations


def test_generates_skill_recommendation():
    ats_result = {
        "missing_skills": ["Power BI"],
        "missing_qualifications": [],
        "missing_keywords": [],
    }

    result = generate_recommendations(ats_result)

    assert len(result["recommendations"]) == 1

    recommendation = result["recommendations"][0]

    assert recommendation["type"] == "skill"
    assert recommendation["item"] == "Power BI"
    assert "Power BI" in recommendation["recommendation"]


def test_generates_multiple_skill_recommendations():
    ats_result = {
        "missing_skills": ["Power BI", "Machine Learning"],
        "missing_qualifications": [],
        "missing_keywords": [],
    }

    result = generate_recommendations(ats_result)

    assert len(result["recommendations"]) == 2

    items = [
        recommendation["item"]
        for recommendation in result["recommendations"]
    ]

    assert items == ["Power BI", "Machine Learning"]


def test_generates_qualification_recommendation():
    ats_result = {
        "missing_skills": [],
        "missing_qualifications": ["Master's degree"],
        "missing_keywords": [],
    }

    result = generate_recommendations(ats_result)

    assert len(result["recommendations"]) == 1

    recommendation = result["recommendations"][0]

    assert recommendation["type"] == "qualification"
    assert recommendation["item"] == "Master's degree"
    assert "qualification" in recommendation["recommendation"].lower()


def test_generates_keyword_recommendation():
    ats_result = {
        "missing_skills": [],
        "missing_qualifications": [],
        "missing_keywords": ["data visualization"],
    }

    result = generate_recommendations(ats_result)

    assert len(result["recommendations"]) == 1

    recommendation = result["recommendations"][0]

    assert recommendation["type"] == "keyword"
    assert recommendation["item"] == "data visualization"
    assert "keyword" in recommendation["recommendation"].lower()


def test_generates_recommendations_for_all_missing_requirements():
    ats_result = {
        "missing_skills": ["Power BI"],
        "missing_qualifications": ["Bachelor's degree"],
        "missing_keywords": ["data visualization"],
    }

    result = generate_recommendations(ats_result)

    assert len(result["recommendations"]) == 3

    assert result["recommendations"][0]["type"] == "skill"
    assert result["recommendations"][1]["type"] == "qualification"
    assert result["recommendations"][2]["type"] == "keyword"


def test_returns_empty_recommendations_when_no_requirements_are_missing():
    ats_result = {
        "missing_skills": [],
        "missing_qualifications": [],
        "missing_keywords": [],
    }

    result = generate_recommendations(ats_result)

    assert result == {
        "recommendations": []
    }


def test_handles_empty_ats_result():
    result = generate_recommendations({})

    assert result == {
        "recommendations": []
    }


def test_handles_none_ats_result():
    result = generate_recommendations(None)

    assert result == {
        "recommendations": []
    }