import pytest
from app.score_engine import (
    calculate_ats_score,
    calculate_experience_score,
    calculate_keyword_score,
    calculate_normalized_weights,
    calculate_qualification_score,
    calculate_skill_score,
)


def test_perfect_match():
    skill_result = {
        "matched": ["Python", "SQL"],
        "missing": [],
    }

    experience_result = {
        "required_years": 3,
        "candidate_years": 5,
        "meets_requirement": True,
    }

    qualification_result = {
        "matched": ["Bachelor's degree"],
        "missing": [],
    }

    keyword_result = {
        "matched": ["python", "sql", "analyst"],
        "missing": [],
    }

    result = calculate_ats_score(
        skill_result,
        experience_result,
        qualification_result,
        keyword_result,
    )

    assert result["ats_score"] == 100


def test_zero_match():
    skill_result = {
        "matched": [],
        "missing": ["Python", "SQL"],
    }

    experience_result = {
        "required_years": 5,
        "candidate_years": 2,
        "meets_requirement": False,
    }

    qualification_result = {
        "matched": [],
        "missing": ["Bachelor's degree"],
    }

    keyword_result = {
        "matched": [],
        "missing": ["python", "sql"],
    }

    result = calculate_ats_score(
        skill_result,
        experience_result,
        qualification_result,
        keyword_result,
    )

    assert result["ats_score"] == 0


def test_skill_score():
    result = calculate_skill_score(
        {
            "matched": ["Python", "SQL"],
            "missing": ["Power BI"],
        }
    )

    assert result == pytest.approx(200 / 3)


def test_qualification_score():
    result = calculate_qualification_score(
        {
            "matched": ["Bachelor's degree"],
            "missing": ["Ph.D."],
        }
    )

    assert result == 50.0


def test_keyword_score():
    result = calculate_keyword_score(
        {
            "matched": ["python", "sql", "analyst"],
            "missing": ["dashboard"],
        }
    )

    assert result == 75.0


def test_experience_score_when_requirement_met():
    result = calculate_experience_score(
        {
            "required_years": 3,
            "candidate_years": 4,
            "meets_requirement": True,
        }
    )

    assert result == 100.0


def test_experience_score_when_requirement_not_met():
    result = calculate_experience_score(
        {
            "required_years": 5,
            "candidate_years": 3,
            "meets_requirement": False,
        }
    )

    assert result == 0.0


def test_no_experience_requirement():
    result = calculate_experience_score(
        {
            "required_years": None,
            "candidate_years": 4,
            "meets_requirement": True,
        }
    )

    assert result is None


def test_no_qualification_requirement():
    result = calculate_qualification_score(
        {
            "matched": [],
            "missing": [],
        }
    )

    assert result is None


def test_no_skill_requirement():
    result = calculate_skill_score(
        {
            "matched": [],
            "missing": [],
        }
    )

    assert result is None


def test_no_keyword_requirement():
    result = calculate_keyword_score(
        {
            "matched": [],
            "missing": [],
        }
    )

    assert result is None


def test_dynamic_weights_without_qualifications():
    component_scores = {
        "skills": 80.0,
        "experience": 100.0,
        "qualifications": None,
        "keywords": 60.0,
    }

    weights = calculate_normalized_weights(
        component_scores
    )

    assert round(weights["skills"], 2) == 58.82
    assert round(weights["experience"], 2) == 23.53
    assert round(weights["keywords"], 2) == 17.65
    assert "qualifications" not in weights


def test_all_components_unavailable():
    result = calculate_ats_score(
        None,
        None,
        None,
        None,
    )

    assert result["ats_score"] == 0
    assert result["weights"] == {}


def test_score_is_between_zero_and_hundred():
    skill_result = {
        "matched": ["Python"],
        "missing": ["SQL"],
    }

    experience_result = {
        "required_years": 3,
        "candidate_years": 4,
        "meets_requirement": True,
    }

    qualification_result = {
        "matched": ["Bachelor's degree"],
        "missing": [],
    }

    keyword_result = {
        "matched": ["python"],
        "missing": ["sql"],
    }

    result = calculate_ats_score(
        skill_result,
        experience_result,
        qualification_result,
        keyword_result,
    )

    assert 0 <= result["ats_score"] <= 100


def test_score_rounding():
    skill_result = {
        "matched": ["Python"],
        "missing": ["SQL"],
    }

    experience_result = {
        "required_years": None,
        "candidate_years": None,
        "meets_requirement": True,
    }

    qualification_result = {
        "matched": [],
        "missing": [],
    }

    keyword_result = {
        "matched": ["python"],
        "missing": ["sql"],
    }

    result = calculate_ats_score(
        skill_result,
        experience_result,
        qualification_result,
        keyword_result,
    )

    assert isinstance(result["ats_score"], int)