import pytest

from app.rag.models import (
    GroundedEvidence,
    RAGContext,
)
from app.rag.optimization.adapter import (
    RAGOptimizationAdapter,
)


def make_evidence(
    evidence_id="evidence:0",
    text="Python Flask REST API experience",
):
    return GroundedEvidence(
        evidence_id=evidence_id,
        text=text,
        source_chunk_ids=[
            "resume:experience:0"
        ],
        claim=text,
        confidence=0.9,
        metadata={
            "section": "experience"
        },
    )


def make_context(
    recommendations=None,
    evidence=None,
    metadata=None,
):
    return RAGContext(
        retrieved_chunks=[],
        evidence=evidence or [],
        recommendations=(
            recommendations or []
        ),
        metadata=metadata or {},
    )


def make_recommendation(
    evidence_id="evidence:0",
    message="Emphasize Python experience.",
    category=None,
    value=None,
):
    recommendation = {
        "type": "emphasis",
        "message": message,
        "evidence_id": evidence_id,
        "source_chunk_ids": [
            "resume:experience:0"
        ],
        "confidence": 0.9,
    }

    if category is not None:
        recommendation["category"] = category

    if value is not None:
        recommendation["value"] = value

    return recommendation


def test_adapts_rag_context():
    evidence = make_evidence()

    recommendation = make_recommendation(
        evidence_id="evidence:0"
    )

    context = make_context(
        recommendations=[recommendation],
        evidence=[evidence],
    )

    result = RAGOptimizationAdapter().adapt(
        context
    )

    assert result["recommendations"] == [
        recommendation
    ]

    assert len(result["evidence"]) == 1


def test_preserves_evidence_fields():
    evidence = make_evidence()

    context = make_context(
        evidence=[evidence]
    )

    result = RAGOptimizationAdapter().adapt(
        context
    )

    adapted = result["evidence"][0]

    assert adapted["evidence_id"] == (
        "evidence:0"
    )
    assert adapted["text"] == (
        "Python Flask REST API experience"
    )
    assert adapted["claim"] == (
        "Python Flask REST API experience"
    )
    assert adapted["confidence"] == 0.9
    assert adapted["source_chunk_ids"] == [
        "resume:experience:0"
    ]


def test_extracts_skill_recommendations():
    recommendation = make_recommendation(
        category="skill",
        value="Python",
    )

    context = make_context(
        recommendations=[recommendation]
    )

    result = RAGOptimizationAdapter().adapt(
        context
    )

    assert result["skills_to_emphasize"] == [
        "Python"
    ]


def test_extracts_experience_recommendations():
    recommendation = make_recommendation(
        category="experience",
        value="REST API development",
    )

    context = make_context(
        recommendations=[recommendation]
    )

    result = RAGOptimizationAdapter().adapt(
        context
    )

    assert result["experience_to_emphasize"] == [
        "REST API development"
    ]


def test_supports_multiple_values():
    recommendation = make_recommendation(
        category="skill",
        value=[
            "Python",
            "Flask",
            "REST API",
        ],
    )

    context = make_context(
        recommendations=[recommendation]
    )

    result = RAGOptimizationAdapter().adapt(
        context
    )

    assert result["skills_to_emphasize"] == [
        "Python",
        "Flask",
        "REST API",
    ]


def test_deduplicates_terms():
    recommendations = [
        make_recommendation(
            category="skill",
            value="Python",
        ),
        make_recommendation(
            category="skill",
            value="Python",
        ),
    ]

    context = make_context(
        recommendations=recommendations
    )

    result = RAGOptimizationAdapter().adapt(
        context
    )

    assert result["skills_to_emphasize"] == [
        "Python"
    ]


def test_ignores_uncategorized_recommendations():
    recommendation = make_recommendation()

    context = make_context(
        recommendations=[recommendation]
    )

    result = RAGOptimizationAdapter().adapt(
        context
    )

    assert result["skills_to_emphasize"] == []
    assert result["experience_to_emphasize"] == []


def test_preserves_metadata():
    context = make_context(
        metadata={
            "source": "rag",
            "recommendation_count": 2,
        }
    )

    result = RAGOptimizationAdapter().adapt(
        context
    )

    assert result["metadata"] == {
        "source": "rag",
        "recommendation_count": 2,
    }


def test_empty_context_produces_empty_payload():
    context = make_context()

    result = RAGOptimizationAdapter().adapt(
        context
    )

    assert result["skills_to_emphasize"] == []
    assert result["experience_to_emphasize"] == []
    assert result["evidence"] == []
    assert result["recommendations"] == []


def test_rejects_invalid_context():
    adapter = RAGOptimizationAdapter()

    with pytest.raises(TypeError):
        adapter.adapt("invalid")


def test_defensively_copies_recommendations():
    recommendation = make_recommendation()

    context = make_context(
        recommendations=[recommendation]
    )

    result = RAGOptimizationAdapter().adapt(
        context
    )

    recommendation["message"] = "changed"

    assert result["recommendations"][0][
        "message"
    ] != "changed"


def test_defensively_copies_metadata():
    metadata = {
        "source": "rag"
    }

    context = make_context(
        metadata=metadata
    )

    result = RAGOptimizationAdapter().adapt(
        context
    )

    metadata["source"] = "changed"

    assert result["metadata"]["source"] == (
        "rag"
    )


def test_defensively_copies_evidence_metadata():
    evidence = make_evidence()

    context = make_context(
        evidence=[evidence]
    )

    result = RAGOptimizationAdapter().adapt(
        context
    )

    evidence.metadata["section"] = (
        "changed"
    )

    assert result["evidence"][0][
        "metadata"
    ]["section"] == "experience"


def test_ignores_empty_recommendation_values():
    recommendation = make_recommendation(
        category="skill",
        value="   ",
    )

    context = make_context(
        recommendations=[recommendation]
    )

    result = RAGOptimizationAdapter().adapt(
        context
    )

    assert result["skills_to_emphasize"] == []