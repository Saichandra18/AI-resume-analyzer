import pytest

from app.rag.models import GroundedEvidence
from app.rag.recommendations.builder import RecommendationBuilder


def make_evidence(
    evidence_id="evidence:0",
    text="Python Flask REST API experience",
    claim="Python Flask REST API experience",
    confidence=0.9,
):
    return GroundedEvidence(
        evidence_id=evidence_id,
        text=text,
        source_chunk_ids=["resume:experience:0"],
        claim=claim,
        confidence=confidence,
        metadata={"section": "experience"},
    )


def test_builds_recommendation():
    builder = RecommendationBuilder()

    results = builder.build(
        [make_evidence()]
    )

    assert len(results) == 1


def test_recommendation_has_expected_type():
    builder = RecommendationBuilder()

    result = builder.build(
        [make_evidence()]
    )[0]

    assert result["type"] == "emphasis"


def test_recommendation_preserves_evidence_id():
    builder = RecommendationBuilder()

    result = builder.build(
        [
            make_evidence(
                evidence_id="evidence:7"
            )
        ]
    )[0]

    assert result["evidence_id"] == "evidence:7"


def test_recommendation_preserves_source_chunks():
    builder = RecommendationBuilder()

    result = builder.build(
        [make_evidence()]
    )[0]

    assert result["source_chunk_ids"] == [
        "resume:experience:0"
    ]


def test_recommendation_preserves_confidence():
    builder = RecommendationBuilder()

    result = builder.build(
        [
            make_evidence(
                confidence=0.75
            )
        ]
    )[0]

    assert result["confidence"] == 0.75


def test_recommendation_preserves_metadata():
    builder = RecommendationBuilder()

    result = builder.build(
        [make_evidence()]
    )[0]

    assert result["metadata"]["section"] == (
        "experience"
    )


def test_matches_requirement():
    builder = RecommendationBuilder()

    result = builder.build(
        [make_evidence()],
        requirements=["Flask"],
    )[0]

    assert "Flask" in result["message"]
    assert "Emphasize" in result["message"]


def test_supports_dictionary_requirements():
    builder = RecommendationBuilder()

    result = builder.build(
        [make_evidence()],
        requirements=[
            {
                "requirement": "REST API",
            }
        ],
    )[0]

    assert "REST API" in result["message"]


def test_rejects_invalid_evidence():
    builder = RecommendationBuilder()

    with pytest.raises(TypeError):
        builder.build(["invalid"])


def test_rejects_invalid_requirements():
    builder = RecommendationBuilder()

    with pytest.raises(TypeError):
        builder.build(
            [make_evidence()],
            requirements="Flask",
        )