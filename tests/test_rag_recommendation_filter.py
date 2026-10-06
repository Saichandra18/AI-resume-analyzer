import pytest

from app.rag.models import GroundedEvidence
from app.rag.recommendations.builder import (
    RecommendationBuilder,
)
from app.rag.recommendations.filter import (
    SafeRecommendationFilter,
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


def make_recommendation(evidence):
    return RecommendationBuilder().build(
        [evidence]
    )[0]


def test_keeps_safe_recommendations():
    evidence = make_evidence()

    recommendation = make_recommendation(
        evidence
    )

    safe, results = SafeRecommendationFilter().filter(
        [recommendation],
        [evidence],
    )

    assert len(safe) == 1
    assert safe[0] == recommendation
    assert len(results) == 1
    assert results[0].safe is True


def test_rejects_unsafe_recommendations():
    evidence = make_evidence(
        text="Python Flask experience",
        claim="Python Flask experience",
    )

    recommendation = make_recommendation(
        evidence
    )

    recommendation["message"] = (
        "Emphasize Python Kubernetes experience."
    )

    safe, results = SafeRecommendationFilter().filter(
        [recommendation],
        [evidence],
    )

    assert safe == []
    assert len(results) == 1
    assert results[0].safe is False
    assert "kubernetes" in (
        results[0].unsupported_terms
    )


def test_mixes_safe_and_unsafe_recommendations():
    evidence_one = make_evidence(
        evidence_id="evidence:1",
        text="Python experience",
        claim="Python experience",
    )

    evidence_two = make_evidence(
        evidence_id="evidence:2",
        text="Flask experience",
        claim="Flask experience",
    )

    safe_recommendation = make_recommendation(
        evidence_one
    )

    unsafe_recommendation = make_recommendation(
        evidence_two
    )

    unsafe_recommendation["message"] = (
        "Emphasize Flask Kubernetes experience."
    )

    safe, results = SafeRecommendationFilter().filter(
        [
            safe_recommendation,
            unsafe_recommendation,
        ],
        [
            evidence_one,
            evidence_two,
        ],
    )

    assert safe == [
        safe_recommendation
    ]

    assert len(results) == 2
    assert results[0].safe is True
    assert results[1].safe is False


def test_empty_recommendations_return_empty_results():
    evidence = make_evidence()

    safe, results = SafeRecommendationFilter().filter(
        [],
        [evidence],
    )

    assert safe == []
    assert results == []


def test_rejects_invalid_recommendations():
    evidence = make_evidence()

    with pytest.raises(TypeError):
        SafeRecommendationFilter().filter(
            "invalid",
            [evidence],
        )


def test_rejects_invalid_evidence():
    recommendation = make_recommendation(
        make_evidence()
    )

    with pytest.raises(TypeError):
        SafeRecommendationFilter().filter(
            [recommendation],
            "invalid",
        )


def test_rejects_invalid_evidence_items():
    recommendation = make_recommendation(
        make_evidence()
    )

    with pytest.raises(TypeError):
        SafeRecommendationFilter().filter(
            [recommendation],
            ["invalid"],
        )


def test_rejects_invalid_recommendation_items():
    evidence = make_evidence()

    with pytest.raises(TypeError):
        SafeRecommendationFilter().filter(
            ["invalid"],
            [evidence],
        )


def test_rejects_unknown_evidence_reference():
    evidence = make_evidence()

    recommendation = make_recommendation(
        evidence
    )

    recommendation["evidence_id"] = (
        "evidence:999"
    )

    with pytest.raises(ValueError):
        SafeRecommendationFilter().filter(
            [recommendation],
            [evidence],
        )


def test_preserves_recommendation_order():
    evidence_one = make_evidence(
        evidence_id="evidence:1",
        text="Python experience",
        claim="Python experience",
    )

    evidence_two = make_evidence(
        evidence_id="evidence:2",
        text="Flask experience",
        claim="Flask experience",
    )

    evidence_three = make_evidence(
        evidence_id="evidence:3",
        text="Docker experience",
        claim="Docker experience",
    )

    recommendations = [
        make_recommendation(evidence_one),
        make_recommendation(evidence_two),
        make_recommendation(evidence_three),
    ]

    safe, results = SafeRecommendationFilter().filter(
        recommendations,
        [
            evidence_one,
            evidence_two,
            evidence_three,
        ],
    )

    assert safe == recommendations
    assert [
        result.evidence_id
        for result in results
    ] == [
        "evidence:1",
        "evidence:2",
        "evidence:3",
    ]


def test_supports_custom_evaluator():
    class DummyResult:
        def __init__(self, safe):
            self.safe = safe

    class DummyEvaluator:
        def evaluate(
            self,
            recommendation,
            evidence,
        ):
            return DummyResult(True)

    evidence = make_evidence()
    recommendation = make_recommendation(
        evidence
    )

    safe, results = SafeRecommendationFilter(
        evaluator=DummyEvaluator()
    ).filter(
        [recommendation],
        [evidence],
    )

    assert safe == [recommendation]
    assert results[0].safe is True