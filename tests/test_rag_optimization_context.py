import pytest

from app.rag.models import (
    GroundedEvidence,
    RetrievedChunk,
)
from app.rag.optimization.context import (
    OptimizationRAGContextBuilder,
)
from app.rag.recommendations.safety import (
    RecommendationSafetyResult,
)


def make_chunk(
    chunk_id="resume:experience:0",
    text="Python Flask REST API experience",
):
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="resume",
        text=text,
        score=0.9,
        metadata={
            "section": "experience"
        },
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


def make_recommendation(
    evidence_id="evidence:0",
    message=(
        "Emphasize Python Flask REST API "
        "experience."
    ),
):
    return {
        "type": "emphasis",
        "message": message,
        "evidence_id": evidence_id,
        "source_chunk_ids": [
            "resume:experience:0"
        ],
        "confidence": 0.9,
    }


def make_safe_result(
    evidence_id="evidence:0",
    safe=True,
):
    return RecommendationSafetyResult(
        safe=safe,
        recommendation=make_recommendation(
            evidence_id=evidence_id
        ),
        evidence_id=evidence_id,
    )


def test_builds_optimization_context():
    builder = OptimizationRAGContextBuilder()

    context = builder.build(
        jd_analysis={
            "required_skills": [
                "Python",
                "Flask",
            ]
        },
        retrieved_chunks=[
            make_chunk()
        ],
        evidence=[
            make_evidence()
        ],
        recommendations=[
            make_recommendation()
        ],
    )

    assert len(context.retrieved_chunks) == 1
    assert len(context.evidence) == 1
    assert len(context.recommendations) == 1


def test_preserves_jd_analysis_in_metadata():
    builder = OptimizationRAGContextBuilder()

    jd_analysis = {
        "required_skills": [
            "Python",
            "Flask",
        ]
    }

    context = builder.build(
        jd_analysis=jd_analysis,
        retrieved_chunks=[],
        evidence=[],
        recommendations=[],
    )

    assert context.metadata[
        "jd_analysis"
    ] == jd_analysis


def test_filters_unsafe_recommendations():
    builder = OptimizationRAGContextBuilder()

    safe = make_recommendation(
        evidence_id="evidence:1"
    )

    unsafe = make_recommendation(
        evidence_id="evidence:2",
        message=(
            "Emphasize Python Kubernetes "
            "experience."
        ),
    )

    context = builder.build(
        jd_analysis={
            "required_skills": [
                "Python"
            ]
        },
        retrieved_chunks=[
            make_chunk(
                chunk_id="resume:experience:1",
                text="Python experience",
            ),
            make_chunk(
                chunk_id="resume:experience:2",
                text="Python experience",
            ),
        ],
        evidence=[
            make_evidence(
                evidence_id="evidence:1",
                text="Python experience",
            ),
            make_evidence(
                evidence_id="evidence:2",
                text="Python experience",
            ),
        ],
        recommendations=[
            safe,
            unsafe,
        ],
        safety_results=[
            make_safe_result(
                evidence_id="evidence:1",
                safe=True,
            ),
            make_safe_result(
                evidence_id="evidence:2",
                safe=False,
            ),
        ],
    )

    assert context.recommendations == [
        safe
    ]


def test_preserves_all_recommendations_without_safety_results():
    builder = OptimizationRAGContextBuilder()

    recommendations = [
        make_recommendation(
            evidence_id="evidence:1"
        ),
        make_recommendation(
            evidence_id="evidence:2"
        ),
    ]

    context = builder.build(
        jd_analysis={},
        retrieved_chunks=[],
        evidence=[],
        recommendations=recommendations,
    )

    assert context.recommendations == (
        recommendations
    )


def test_records_recommendation_count():
    builder = OptimizationRAGContextBuilder()

    context = builder.build(
        jd_analysis={},
        retrieved_chunks=[],
        evidence=[],
        recommendations=[
            make_recommendation()
        ],
    )

    assert context.metadata[
        "recommendation_count"
    ] == 1


def test_records_evidence_count():
    builder = OptimizationRAGContextBuilder()

    context = builder.build(
        jd_analysis={},
        retrieved_chunks=[
            make_chunk()
        ],
        evidence=[
            make_evidence()
        ],
        recommendations=[],
    )

    assert context.metadata[
        "evidence_count"
    ] == 1


def test_preserves_custom_metadata():
    builder = OptimizationRAGContextBuilder()

    context = builder.build(
        jd_analysis={},
        retrieved_chunks=[],
        evidence=[],
        recommendations=[],
        metadata={
            "source": "rag"
        },
    )

    assert context.metadata[
        "source"
    ] == "rag"


def test_rejects_invalid_jd_analysis():
    builder = OptimizationRAGContextBuilder()

    with pytest.raises(TypeError):
        builder.build(
            jd_analysis="invalid",
            retrieved_chunks=[],
            evidence=[],
            recommendations=[],
        )


def test_rejects_invalid_chunks():
    builder = OptimizationRAGContextBuilder()

    with pytest.raises(TypeError):
        builder.build(
            jd_analysis={},
            retrieved_chunks=["invalid"],
            evidence=[],
            recommendations=[],
        )


def test_rejects_invalid_evidence():
    builder = OptimizationRAGContextBuilder()

    with pytest.raises(TypeError):
        builder.build(
            jd_analysis={},
            retrieved_chunks=[],
            evidence=["invalid"],
            recommendations=[],
        )


def test_rejects_invalid_recommendations():
    builder = OptimizationRAGContextBuilder()

    with pytest.raises(TypeError):
        builder.build(
            jd_analysis={},
            retrieved_chunks=[],
            evidence=[],
            recommendations=["invalid"],
        )


def test_rejects_invalid_safety_results():
    builder = OptimizationRAGContextBuilder()

    with pytest.raises(TypeError):
        builder.build(
            jd_analysis={},
            retrieved_chunks=[],
            evidence=[],
            recommendations=[],
            safety_results=["invalid"],
        )


def test_rejects_invalid_metadata():
    builder = OptimizationRAGContextBuilder()

    with pytest.raises(TypeError):
        builder.build(
            jd_analysis={},
            retrieved_chunks=[],
            evidence=[],
            recommendations=[],
            metadata="invalid",
        )