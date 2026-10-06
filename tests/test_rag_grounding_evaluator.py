"""Tests for RAG evidence and grounding evaluation."""

import pytest

from app.rag.evaluation.grounding import GroundingEvaluator
from app.rag.models import (
    GroundedEvidence,
    RetrievedChunk,
)
from app.rag.recommendations.safety import (
    RecommendationSafetyResult,
)


def chunk(chunk_id):
    return RetrievedChunk(
        chunk_id=chunk_id,
        text=f"source text for {chunk_id}",
        score=0.9,
    )


def evidence(
    evidence_id,
    source_ids,
    claim="Python",
):
    return GroundedEvidence(
        evidence_id=evidence_id,
        text=f"{claim} experience",
        source_chunk_ids=source_ids,
        claim=claim,
        confidence=0.9,
    )


def safe_result(evidence_id="e-1"):
    return RecommendationSafetyResult(
        safe=True,
        recommendation={
            "message": "Emphasize Python experience.",
            "evidence_id": evidence_id,
            "source_chunk_ids": ["chunk-1"],
            "confidence": 0.9,
        },
        evidence_id=evidence_id,
    )


def unsafe_result(evidence_id="e-2"):
    return RecommendationSafetyResult(
        safe=False,
        recommendation={
            "message": "Unsupported claim.",
            "evidence_id": evidence_id,
            "source_chunk_ids": ["chunk-2"],
            "confidence": 0.5,
        },
        reason="Unsupported claim.",
        evidence_id=evidence_id,
    )


def test_all_evidence_is_grounded():
    evaluator = GroundingEvaluator()

    result = evaluator.evaluate_evidence(
        [
            evidence(
                "e-1",
                ["chunk-1"],
            ),
            evidence(
                "e-2",
                ["chunk-2"],
            ),
        ],
        [
            chunk("chunk-1"),
            chunk("chunk-2"),
        ],
    )

    assert result["evidence_count"] == 2
    assert result["grounded_evidence_count"] == 2
    assert result["invalid_evidence_count"] == 0
    assert result["grounding_rate"] == pytest.approx(1.0)


def test_partially_grounded_evidence():
    evaluator = GroundingEvaluator()

    result = evaluator.evaluate_evidence(
        [
            evidence(
                "e-1",
                ["chunk-1"],
            ),
            evidence(
                "e-2",
                ["missing"],
            ),
        ],
        [
            chunk("chunk-1"),
        ],
    )

    assert result["grounded_evidence_count"] == 1
    assert result["invalid_evidence_count"] == 1
    assert result["grounding_rate"] == pytest.approx(0.5)


def test_no_evidence():
    evaluator = GroundingEvaluator()

    result = evaluator.evaluate_evidence(
        [],
        [
            chunk("chunk-1"),
        ],
    )

    assert result["evidence_count"] == 0
    assert result["grounded_evidence_count"] == 0
    assert result["grounding_rate"] == 0.0


def test_evidence_coverage_contains_source_counts():
    evaluator = GroundingEvaluator()

    result = evaluator.evaluate_evidence(
        [
            evidence(
                "e-1",
                [
                    "chunk-1",
                    "chunk-2",
                ],
            ),
        ],
        [
            chunk("chunk-1"),
            chunk("chunk-2"),
        ],
    )

    coverage = result["evidence_coverage"][0]

    assert coverage["evidence_id"] == "e-1"
    assert coverage["source_chunk_count"] == 2
    assert coverage["matched_chunk_count"] == 2
    assert coverage["grounded"] is True


def test_safety_allows_all_safe_results():
    evaluator = GroundingEvaluator()

    result = evaluator.evaluate_safety(
        [
            safe_result("e-1"),
            safe_result("e-2"),
        ]
    )

    assert result["recommendation_count"] == 2
    assert result["safe_count"] == 2
    assert result["unsafe_count"] == 0
    assert result["safety_rate"] == pytest.approx(1.0)


def test_safety_counts_unsafe_results():
    evaluator = GroundingEvaluator()

    result = evaluator.evaluate_safety(
        [
            safe_result("e-1"),
            unsafe_result("e-2"),
        ]
    )

    assert result["recommendation_count"] == 2
    assert result["safe_count"] == 1
    assert result["unsafe_count"] == 1
    assert result["safety_rate"] == pytest.approx(0.5)


def test_empty_safety_results():
    evaluator = GroundingEvaluator()

    result = evaluator.evaluate_safety([])

    assert result["recommendation_count"] == 0
    assert result["safe_count"] == 0
    assert result["unsafe_count"] == 0
    assert result["safety_rate"] == 0.0


def test_combined_evaluation():
    evaluator = GroundingEvaluator()

    result = evaluator.evaluate(
        evidence=[
            evidence(
                "e-1",
                ["chunk-1"],
            ),
        ],
        retrieved_chunks=[
            chunk("chunk-1"),
        ],
        safety_results=[
            safe_result("e-1"),
        ],
    )

    assert result["overall_grounding_rate"] == pytest.approx(1.0)
    assert result["overall_safety_rate"] == pytest.approx(1.0)
    assert result["evidence"]["grounded_evidence_count"] == 1
    assert result["safety"]["safe_count"] == 1


def test_combined_evaluation_with_unsafe_result():
    evaluator = GroundingEvaluator()

    result = evaluator.evaluate(
        evidence=[
            evidence(
                "e-1",
                ["chunk-1"],
            ),
        ],
        retrieved_chunks=[
            chunk("chunk-1"),
        ],
        safety_results=[
            unsafe_result("e-1"),
        ],
    )

    assert result["overall_grounding_rate"] == pytest.approx(1.0)
    assert result["overall_safety_rate"] == pytest.approx(0.0)


def test_invalid_evidence_collection():
    evaluator = GroundingEvaluator()

    with pytest.raises(TypeError):
        evaluator.evaluate_evidence(
            None,
            [],
        )


def test_invalid_evidence_item():
    evaluator = GroundingEvaluator()

    with pytest.raises(TypeError):
        evaluator.evaluate_evidence(
            ["invalid"],
            [],
        )


def test_invalid_retrieved_collection():
    evaluator = GroundingEvaluator()

    with pytest.raises(TypeError):
        evaluator.evaluate_evidence(
            [],
            None,
        )


def test_invalid_retrieved_item():
    evaluator = GroundingEvaluator()

    with pytest.raises(TypeError):
        evaluator.evaluate_evidence(
            [],
            ["invalid"],
        )


def test_invalid_safety_collection():
    evaluator = GroundingEvaluator()

    with pytest.raises(TypeError):
        evaluator.evaluate_safety(None)


def test_invalid_safety_item():
    evaluator = GroundingEvaluator()

    with pytest.raises(TypeError):
        evaluator.evaluate_safety(
            ["invalid"]
        )


def test_multiple_source_chunks_can_ground_evidence():
    evaluator = GroundingEvaluator()

    result = evaluator.evaluate_evidence(
        [
            evidence(
                "e-1",
                [
                    "chunk-1",
                    "chunk-2",
                    "chunk-3",
                ],
            ),
        ],
        [
            chunk("chunk-1"),
            chunk("chunk-2"),
            chunk("chunk-3"),
        ],
    )

    assert result["grounding_rate"] == pytest.approx(1.0)
    assert result["evidence_coverage"][0][
        "matched_chunk_count"
    ] == 3