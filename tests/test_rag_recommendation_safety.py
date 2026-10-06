import pytest

from app.rag.recommendations.safety import (
    RecommendationSafetyResult,
)


def make_recommendation():
    return {
        "type": "emphasis",
        "message": (
            "Emphasize Python Flask experience."
        ),
        "evidence_id": "evidence:0",
        "source_chunk_ids": [
            "resume:experience:0"
        ],
        "confidence": 0.9,
    }


def test_creates_safe_result():
    result = RecommendationSafetyResult(
        safe=True,
        recommendation=make_recommendation(),
        evidence_id="evidence:0",
    )

    assert result.safe is True
    assert result.evidence_id == "evidence:0"


def test_creates_unsafe_result():
    result = RecommendationSafetyResult(
        safe=False,
        recommendation=make_recommendation(),
        reason="Unsupported claim.",
        unsupported_terms=[
            "kubernetes"
        ],
        evidence_id="evidence:0",
    )

    assert result.safe is False
    assert result.reason == "Unsupported claim."
    assert result.unsupported_terms == [
        "kubernetes"
    ]


def test_defaults_optional_values():
    result = RecommendationSafetyResult(
        safe=True
    )

    assert result.recommendation is None
    assert result.reason is None
    assert result.unsupported_terms == []
    assert result.evidence_id is None
    assert result.metadata == {}


def test_to_dict():
    result = RecommendationSafetyResult(
        safe=False,
        recommendation=make_recommendation(),
        reason="Unsupported claim.",
        unsupported_terms=[
            "kubernetes"
        ],
        evidence_id="evidence:0",
        metadata={
            "section": "experience"
        },
    )

    data = result.to_dict()

    assert data["safe"] is False
    assert data["reason"] == "Unsupported claim."
    assert data["unsupported_terms"] == [
        "kubernetes"
    ]
    assert data["evidence_id"] == "evidence:0"
    assert data["metadata"]["section"] == (
        "experience"
    )


def test_from_dict():
    data = {
        "safe": False,
        "recommendation": make_recommendation(),
        "reason": "Unsupported claim.",
        "unsupported_terms": [
            "kubernetes"
        ],
        "evidence_id": "evidence:0",
        "metadata": {
            "section": "experience"
        },
    }

    result = RecommendationSafetyResult.from_dict(
        data
    )

    assert result.safe is False
    assert result.reason == "Unsupported claim."
    assert result.unsupported_terms == [
        "kubernetes"
    ]


def test_round_trip():
    original = RecommendationSafetyResult(
        safe=True,
        recommendation=make_recommendation(),
        evidence_id="evidence:0",
        metadata={
            "source": "rag"
        },
    )

    restored = RecommendationSafetyResult.from_dict(
        original.to_dict()
    )

    assert restored.to_dict() == (
        original.to_dict()
    )


def test_defensive_copy_of_recommendation():
    recommendation = make_recommendation()

    result = RecommendationSafetyResult(
        safe=True,
        recommendation=recommendation,
    )

    recommendation["message"] = "changed"

    assert result.recommendation["message"] != (
        "changed"
    )


def test_defensive_copy_of_metadata():
    metadata = {
        "section": "experience"
    }

    result = RecommendationSafetyResult(
        safe=True,
        metadata=metadata,
    )

    metadata["section"] = "education"

    assert result.metadata["section"] == (
        "experience"
    )


def test_rejects_invalid_safe_value():
    with pytest.raises(TypeError):
        RecommendationSafetyResult(
            safe="true"
        )


def test_rejects_invalid_recommendation():
    with pytest.raises(TypeError):
        RecommendationSafetyResult(
            safe=True,
            recommendation="invalid",
        )


def test_rejects_invalid_reason():
    with pytest.raises(TypeError):
        RecommendationSafetyResult(
            safe=True,
            reason=123,
        )


def test_rejects_invalid_unsupported_terms():
    with pytest.raises(TypeError):
        RecommendationSafetyResult(
            safe=True,
            unsupported_terms="kubernetes",
        )


def test_rejects_invalid_evidence_id():
    with pytest.raises(TypeError):
        RecommendationSafetyResult(
            safe=True,
            evidence_id=123,
        )


def test_rejects_invalid_metadata():
    with pytest.raises(TypeError):
        RecommendationSafetyResult(
            safe=True,
            metadata="invalid",
        )