from app.qualification_matcher import (
    degree_matches,
    get_degree_family,
    match_qualifications,
    normalize_qualification,
)


def test_bachelors_degree_matches_btech():
    assert degree_matches(
        "B.Tech",
        "Bachelor's degree",
    ) is True


def test_bachelors_degree_matches_be():
    assert degree_matches(
        "B.E.",
        "Bachelor's degree",
    ) is True


def test_bachelors_degree_matches_bsc():
    assert degree_matches(
        "B.Sc.",
        "Bachelor's degree",
    ) is True


def test_masters_degree_matches_mba():
    assert degree_matches(
        "MBA",
        "Master's degree",
    ) is True


def test_masters_degree_matches_mca():
    assert degree_matches(
        "MCA",
        "Master's degree",
    ) is True


def test_doctorate_matches_phd():
    assert degree_matches(
        "Doctorate",
        "Ph.D.",
    ) is True


def test_different_degree_families_do_not_match():
    assert degree_matches(
        "B.Tech",
        "Master's degree",
    ) is False


def test_case_insensitive_normalization():
    assert normalize_qualification("b.tech") == "btech"
    assert normalize_qualification("B.Tech") == "btech"


def test_get_degree_family():
    assert get_degree_family("B.Tech") == "bachelor"
    assert get_degree_family("MBA") == "master"
    assert get_degree_family("Ph.D.") == "doctorate"


def test_basic_qualification_matching():
    resume_degrees = [
        "Bachelor of Technology in Computer Science",
        "MBA",
    ]

    required_qualifications = [
        "Bachelor's degree",
        "Master's degree",
    ]

    result = match_qualifications(
        resume_degrees,
        required_qualifications,
    )

    assert result["matched"] == [
        "Bachelor's degree",
        "Master's degree",
    ]

    assert result["missing"] == []


def test_missing_qualification():
    resume_degrees = [
        "B.Tech"
    ]

    required_qualifications = [
        "Bachelor's degree",
        "Ph.D.",
    ]

    result = match_qualifications(
        resume_degrees,
        required_qualifications,
    )

    assert result["matched"] == [
        "Bachelor's degree"
    ]

    assert result["missing"] == [
        "Ph.D."
    ]


def test_empty_resume_degrees():
    result = match_qualifications(
        [],
        ["Bachelor's degree"],
    )

    assert result["matched"] == []
    assert result["missing"] == [
        "Bachelor's degree"
    ]


def test_empty_required_qualifications():
    result = match_qualifications(
        ["B.Tech"],
        [],
    )

    assert result["matched"] == []
    assert result["missing"] == []


def test_none_inputs():
    result = match_qualifications(None, None)

    assert result["matched"] == []
    assert result["missing"] == []


def test_duplicate_required_qualifications():
    result = match_qualifications(
        ["B.Tech"],
        [
            "Bachelor's degree",
            "Bachelor's degree",
        ],
    )

    assert result["matched"] == [
        "Bachelor's degree"
    ]

    assert result["missing"] == []