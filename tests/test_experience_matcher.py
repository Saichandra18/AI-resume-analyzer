from app.experience_matcher import match_experience


def test_candidate_meets_experience_requirement():
    resume_experience = {
        "years": ["2020 - 2024"]
    }

    required_experience = {
        "min_years": 3
    }

    result = match_experience(
        resume_experience,
        required_experience,
    )

    assert result["required_years"] == 3
    assert result["candidate_years"] == 4
    assert result["meets_requirement"] is True


def test_candidate_does_not_meet_experience_requirement():
    resume_experience = {
        "years": ["2023 - 2025"]
    }

    required_experience = {
        "min_years": 5
    }

    result = match_experience(
        resume_experience,
        required_experience,
    )

    assert result["required_years"] == 5
    assert result["candidate_years"] == 2
    assert result["meets_requirement"] is False


def test_present_experience():
    resume_experience = {
        "years": ["2022 - Present"]
    }

    required_experience = {
        "min_years": 3
    }

    result = match_experience(
        resume_experience,
        required_experience,
    )

    assert result["candidate_years"] >= 3
    assert result["meets_requirement"] is True


def test_current_experience():
    resume_experience = {
        "years": ["2022 - Current"]
    }

    required_experience = {
        "min_years": 3
    }

    result = match_experience(
        resume_experience,
        required_experience,
    )

    assert result["candidate_years"] >= 3
    assert result["meets_requirement"] is True


def test_multiple_non_overlapping_experience_periods():
    resume_experience = {
        "years": [
            "2018 - 2020",
            "2021 - 2024",
        ]
    }

    required_experience = {
        "min_years": 4
    }

    result = match_experience(
        resume_experience,
        required_experience,
    )

    assert result["candidate_years"] == 5
    assert result["meets_requirement"] is True


def test_overlapping_experience_periods_are_not_double_counted():
    resume_experience = {
        "years": [
            "2020 - 2023",
            "2022 - 2025",
        ]
    }

    required_experience = {
        "min_years": 5
    }

    result = match_experience(
        resume_experience,
        required_experience,
    )

    assert result["candidate_years"] == 5
    assert result["meets_requirement"] is True


def test_no_experience_requirement():
    resume_experience = {
        "years": ["2020 - 2024"]
    }

    required_experience = None

    result = match_experience(
        resume_experience,
        required_experience,
    )

    assert result["required_years"] is None
    assert result["candidate_years"] == 4
    assert result["meets_requirement"] is True


def test_resume_experience_information_missing():
    resume_experience = {
        "years": []
    }

    required_experience = {
        "min_years": 3
    }

    result = match_experience(
        resume_experience,
        required_experience,
    )

    assert result["required_years"] == 3
    assert result["candidate_years"] is None
    assert result["meets_requirement"] is False


def test_empty_inputs():
    result = match_experience(None, None)

    assert result["required_years"] is None
    assert result["candidate_years"] is None
    assert result["meets_requirement"] is True


def test_invalid_year_range_is_ignored():
    resume_experience = {
        "years": [
            "invalid range",
            "2020 - 2024",
        ]
    }

    required_experience = {
        "min_years": 3
    }

    result = match_experience(
        resume_experience,
        required_experience,
    )

    assert result["candidate_years"] == 4
    assert result["meets_requirement"] is True