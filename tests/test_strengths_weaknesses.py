from app.strengths_weaknesses import generate_strengths_weaknesses


def complete_ats_result():
    return {
        "matched_skills": ["Python", "SQL"],
        "missing_skills": ["Power BI"],
        "experience": {
            "required_years": 3,
            "candidate_years": 4,
            "meets_requirement": True,
        },
        "matched_qualifications": ["Bachelor's degree"],
        "missing_qualifications": [],
        "matched_keywords": ["data", "analyst"],
        "missing_keywords": ["machine learning"],
    }


def test_generates_skill_strengths():
    result = generate_strengths_weaknesses(
        complete_ats_result()
    )

    strengths = result["strengths"]

    skill_items = [
        item["item"]
        for item in strengths
        if item["type"] == "skill"
    ]

    assert skill_items == ["Python", "SQL"]


def test_generates_missing_skill_weaknesses():
    result = generate_strengths_weaknesses(
        complete_ats_result()
    )

    weaknesses = result["weaknesses"]

    skill_items = [
        item["item"]
        for item in weaknesses
        if item["type"] == "skill"
    ]

    assert skill_items == ["Power BI"]


def test_generates_experience_strength():
    result = generate_strengths_weaknesses(
        complete_ats_result()
    )

    experience_strengths = [
        item
        for item in result["strengths"]
        if item["type"] == "experience"
    ]

    assert len(experience_strengths) == 1
    assert experience_strengths[0]["item"] == "experience"


def test_generates_qualification_strength():
    result = generate_strengths_weaknesses(
        complete_ats_result()
    )

    qualification_strengths = [
        item
        for item in result["strengths"]
        if item["type"] == "qualification"
    ]

    assert len(qualification_strengths) == 1
    assert qualification_strengths[0]["item"] == "Bachelor's degree"


def test_generates_keyword_strengths():
    result = generate_strengths_weaknesses(
        complete_ats_result()
    )

    keyword_items = [
        item["item"]
        for item in result["strengths"]
        if item["type"] == "keyword"
    ]

    assert keyword_items == ["data", "analyst"]


def test_generates_keyword_weaknesses():
    result = generate_strengths_weaknesses(
        complete_ats_result()
    )

    keyword_items = [
        item["item"]
        for item in result["weaknesses"]
        if item["type"] == "keyword"
    ]

    assert keyword_items == ["machine learning"]


def test_generates_experience_weakness_when_requirement_not_met():
    ats_result = {
        "matched_skills": [],
        "missing_skills": [],
        "experience": {
            "required_years": 3,
            "candidate_years": 2,
            "meets_requirement": False,
        },
        "matched_qualifications": [],
        "missing_qualifications": [],
        "matched_keywords": [],
        "missing_keywords": [],
    }

    result = generate_strengths_weaknesses(ats_result)

    experience_weaknesses = [
        item
        for item in result["weaknesses"]
        if item["type"] == "experience"
    ]

    assert len(experience_weaknesses) == 1
    assert experience_weaknesses[0]["item"] == "experience"


def test_generates_qualification_weaknesses():
    ats_result = {
        "matched_skills": [],
        "missing_skills": [],
        "experience": {},
        "matched_qualifications": [],
        "missing_qualifications": ["Master's degree"],
        "matched_keywords": [],
        "missing_keywords": [],
    }

    result = generate_strengths_weaknesses(ats_result)

    qualification_items = [
        item["item"]
        for item in result["weaknesses"]
        if item["type"] == "qualification"
    ]

    assert qualification_items == ["Master's degree"]


def test_returns_empty_sections_when_nothing_is_available():
    result = generate_strengths_weaknesses({})

    assert result == {
        "strengths": [],
        "weaknesses": [],
    }


def test_handles_none_ats_result():
    result = generate_strengths_weaknesses(None)

    assert result == {
        "strengths": [],
        "weaknesses": [],
    }