import pytest

from app.rag.recommendations.claim_detector import (
    UnsupportedClaimDetector,
)


def make_recommendation(
    message="Emphasize Python Flask REST API experience."
):
    return {
        "type": "emphasis",
        "message": message,
        "evidence_id": "evidence:0",
        "source_chunk_ids": [
            "resume:experience:0"
        ],
        "confidence": 0.9,
    }


def test_supported_terms_are_not_flagged():
    detector = UnsupportedClaimDetector()

    result = detector.detect(
        make_recommendation(),
        "Python Flask REST API experience",
    )

    assert result == []


def test_detects_unsupported_skill():
    detector = UnsupportedClaimDetector()

    result = detector.detect(
        make_recommendation(
            "Emphasize Python Kubernetes experience."
        ),
        "Python Flask experience",
    )

    assert "kubernetes" in result


def test_detects_multiple_unsupported_terms():
    detector = UnsupportedClaimDetector()

    result = detector.detect(
        make_recommendation(
            "Emphasize Python Kubernetes Docker experience."
        ),
        "Python Flask experience",
    )

    assert "kubernetes" in result
    assert "docker" in result


def test_comparison_is_case_insensitive():
    detector = UnsupportedClaimDetector()

    result = detector.detect(
        make_recommendation(
            "Emphasize PYTHON and FLASK experience."
        ),
        "python flask experience",
    )

    assert result == []


def test_handles_empty_evidence():
    detector = UnsupportedClaimDetector()

    result = detector.detect(
        make_recommendation(
            "Emphasize Python Flask experience."
        ),
        "",
    )

    assert "python" in result
    assert "flask" in result


def test_empty_recommendation_returns_no_terms():
    detector = UnsupportedClaimDetector()

    result = detector.detect(
        make_recommendation(""),
        "Python Flask experience",
    )

    assert result == []


def test_rejects_invalid_recommendation():
    detector = UnsupportedClaimDetector()

    with pytest.raises(TypeError):
        detector.detect(
            "invalid",
            "Python experience",
        )


def test_rejects_invalid_evidence():
    detector = UnsupportedClaimDetector()

    with pytest.raises(TypeError):
        detector.detect(
            make_recommendation(),
            None,
        )


def test_rejects_invalid_message():
    detector = UnsupportedClaimDetector()

    with pytest.raises(TypeError):
        detector.detect(
            {
                "message": None,
            },
            "Python experience",
        )