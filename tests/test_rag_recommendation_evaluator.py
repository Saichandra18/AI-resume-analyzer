import pytest

from app.rag.models import GroundedEvidence
from app.rag.recommendations.builder import (
    RecommendationBuilder,
)
from app.rag.recommendations.evaluator import (
    RecommendationSafetyEvaluator,
)


def make_evidence(
    evidence_id="evidence:0",
    text="Python Flask REST API experience",
    claim="Python Flask REST API experience",
    confidence=0.9,
):
    return GroundedEvidence(
        evidence_id=evidence_id,
        text=text,
        source_chunk_ids=[
            "resume:experience:0"
        ],
        claim=claim,
        confidence=confidence,
        metadata={
            "section": "experience"
        },
    )


def make_recommendation(
    evidence=None,
    **updates,
):
    evidence = evidence or make_evidence()

    recommendation = RecommendationBuilder().build(
        [evidence]
    )[0]

    recommendation.update(updates)

    return recommendation


def test_safe_recommendation_returns_safe_result():
    evidence = make_evidence()
    recommendation = make_recommendation(
        evidence=evidence
    )

    result = RecommendationSafetyEvaluator().evaluate(
        recommendation,
        evidence,
    )

    assert result.safe is True
    assert result.evidence_id == "evidence:0"


def test_unsupported_claim_returns_unsafe_result():
    evidence = make_evidence(
        text="Python Flask experience",
        claim="Python Flask experience",
    )

    recommendation = make_recommendation(
        evidence=evidence,
        message=(
            "Emphasize Python Kubernetes experience."
        ),
    )

    result = RecommendationSafetyEvaluator().evaluate(
        recommendation,
        evidence,
    )

    assert result.safe is False
    assert "kubernetes" in result.unsupported_terms


def test_mismatched_evidence_returns_unsafe_result():
    evidence = make_evidence(
        evidence_id="evidence:0"
    )

    recommendation = make_recommendation(
        evidence=evidence,
        evidence_id="evidence:999",
    )

    result = RecommendationSafetyEvaluator().evaluate(
        recommendation,
        evidence,
    )

    assert result.safe is False
    assert result.reason == (
        "Recommendation references different evidence."
    )


def test_missing_source_chunks_returns_unsafe_result():
    evidence = make_evidence()

    recommendation = make_recommendation(
        evidence=evidence,
        source_chunk_ids=[],
    )

    result = RecommendationSafetyEvaluator().evaluate(
        recommendation,
        evidence,
    )

    assert result.safe is False


def test_unknown_source_chunk_returns_unsafe_result():
    evidence = make_evidence()

    recommendation = make_recommendation(
        evidence=evidence,
        source_chunk_ids=[
            "resume:experience:999"
        ],
    )

    result = RecommendationSafetyEvaluator().evaluate(
        recommendation,
        evidence,
    )

    assert result.safe is False


def test_empty_message_returns_unsafe_result():
    evidence = make_evidence()

    recommendation = make_recommendation(
        evidence=evidence,
        message="",
    )

    result = RecommendationSafetyEvaluator().evaluate(
        recommendation,
        evidence,
    )

    assert result.safe is False


def test_confidence_mismatch_returns_unsafe_result():
    evidence = make_evidence(
        confidence=0.9
    )

    recommendation = make_recommendation(
        evidence=evidence,
        confidence=0.7,
    )

    result = RecommendationSafetyEvaluator().evaluate(
        recommendation,
        evidence,
    )

    assert result.safe is False


def test_invalid_recommendation_raises_type_error():
    evaluator = RecommendationSafetyEvaluator()

    with pytest.raises(TypeError):
        evaluator.evaluate(
            "invalid",
            make_evidence(),
        )


def test_invalid_evidence_raises_type_error():
    evaluator = RecommendationSafetyEvaluator()

    with pytest.raises(TypeError):
        evaluator.evaluate(
            make_recommendation(),
            "invalid",
        )


def test_invalid_source_chunk_type_raises_type_error():
    evidence = make_evidence()

    recommendation = make_recommendation(
        evidence=evidence,
        source_chunk_ids="resume:experience:0",
    )

    with pytest.raises(TypeError):
        RecommendationSafetyEvaluator().evaluate(
            recommendation,
            evidence,
        )


def test_invalid_message_type_raises_type_error():
    evidence = make_evidence()

    recommendation = make_recommendation(
        evidence=evidence,
        message=None,
    )

    with pytest.raises(TypeError):
        RecommendationSafetyEvaluator().evaluate(
            recommendation,
            evidence,
        )


def test_invalid_confidence_type_raises_type_error():
    evidence = make_evidence()

    recommendation = make_recommendation(
        evidence=evidence,
        confidence="high",
    )

    with pytest.raises(TypeError):
        RecommendationSafetyEvaluator().evaluate(
            recommendation,
            evidence,
        )


def test_invalid_confidence_range_returns_unsafe_result():
    evidence = make_evidence()

    recommendation = make_recommendation(
        evidence=evidence,
        confidence=1.5,
    )

    result = RecommendationSafetyEvaluator().evaluate(
        recommendation,
        evidence,
    )

    assert result.safe is False


def test_safe_result_contains_validation_metadata():
    evidence = make_evidence()

    recommendation = make_recommendation(
        evidence=evidence
    )

    result = RecommendationSafetyEvaluator().evaluate(
        recommendation,
        evidence,
    )

    assert result.metadata["validation"] == (
        "grounded"
    )