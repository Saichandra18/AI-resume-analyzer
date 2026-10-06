import pytest

from app.rag.optimization.phase11_adapter import (
    Phase11OptimizationAdapter,
)
from app.rag.optimization.signals import (
    OptimizationSignal,
    OptimizationSignalSet,
)


def make_signal(
    signal_type="skill",
    value="Python",
    evidence_id="evidence:0",
    source_chunk_ids=None,
    confidence=0.9,
    metadata=None,
):
    return OptimizationSignal(
        signal_type=signal_type,
        value=value,
        evidence_id=evidence_id,
        source_chunk_ids=source_chunk_ids or ["doc:0"],
        confidence=confidence,
        metadata=metadata or {"document_id": "doc"},
    )


def test_adapts_skill_signal():
    adapter = Phase11OptimizationAdapter()

    signal_set = OptimizationSignalSet(
        signals=[
            make_signal(
                signal_type="skill",
                value="Python",
            )
        ]
    )

    result = adapter.adapt(signal_set)

    assert result["skills_to_emphasize"] == ["Python"]
    assert result["experience_to_emphasize"] == []
    assert result["keywords_to_emphasize"] == []
    assert result["emphasis_instructions"] == []


def test_adapts_experience_signal():
    adapter = Phase11OptimizationAdapter()

    signal_set = OptimizationSignalSet(
        signals=[
            make_signal(
                signal_type="experience",
                value="backend development",
            )
        ]
    )

    result = adapter.adapt(signal_set)

    assert result["experience_to_emphasize"] == [
        "backend development"
    ]


def test_adapts_keyword_signal():
    adapter = Phase11OptimizationAdapter()

    signal_set = OptimizationSignalSet(
        signals=[
            make_signal(
                signal_type="keyword",
                value="REST API",
            )
        ]
    )

    result = adapter.adapt(signal_set)

    assert result["keywords_to_emphasize"] == ["REST API"]


def test_adapts_emphasis_signal():
    adapter = Phase11OptimizationAdapter()

    signal_set = OptimizationSignalSet(
        signals=[
            make_signal(
                signal_type="emphasis",
                value="Emphasize API development",
            )
        ]
    )

    result = adapter.adapt(signal_set)

    assert result["emphasis_instructions"] == [
        "Emphasize API development"
    ]


def test_adapts_multiple_signal_types():
    adapter = Phase11OptimizationAdapter()

    signal_set = OptimizationSignalSet(
        signals=[
            make_signal("skill", "Python"),
            make_signal("experience", "backend development"),
            make_signal("keyword", "REST API"),
            make_signal(
                "emphasis",
                "Emphasize measurable impact",
            ),
        ]
    )

    result = adapter.adapt(signal_set)

    assert result["skills_to_emphasize"] == ["Python"]
    assert result["experience_to_emphasize"] == [
        "backend development"
    ]
    assert result["keywords_to_emphasize"] == ["REST API"]
    assert result["emphasis_instructions"] == [
        "Emphasize measurable impact"
    ]


def test_preserves_grounding_information():
    adapter = Phase11OptimizationAdapter()

    signal = make_signal(
        signal_type="skill",
        value="Python",
        evidence_id="evidence:7",
        source_chunk_ids=["doc:2", "doc:3"],
        confidence=0.87,
        metadata={
            "document_id": "doc",
            "source": "resume",
        },
    )

    signal_set = OptimizationSignalSet(
        signals=[signal]
    )

    result = adapter.adapt(signal_set)

    assert result["grounding"] == [
        {
            "signal_type": "skill",
            "value": "Python",
            "evidence_id": "evidence:7",
            "source_chunk_ids": ["doc:2", "doc:3"],
            "confidence": 0.87,
            "metadata": {
                "document_id": "doc",
                "source": "resume",
            },
        }
    ]


def test_preserves_signal_set_metadata():
    adapter = Phase11OptimizationAdapter()

    signal_set = OptimizationSignalSet(
        signals=[make_signal()],
        metadata={
            "jd_id": "jd-001",
            "retrieval_count": 5,
        },
    )

    result = adapter.adapt(signal_set)

    assert result["metadata"] == {
        "jd_id": "jd-001",
        "retrieval_count": 5,
    }


def test_does_not_mutate_signal_set_metadata():
    adapter = Phase11OptimizationAdapter()

    metadata = {
        "jd_id": "jd-001",
    }

    signal_set = OptimizationSignalSet(
        signals=[make_signal()],
        metadata=metadata,
    )

    result = adapter.adapt(signal_set)

    result["metadata"]["jd_id"] = "changed"

    assert signal_set.metadata["jd_id"] == "jd-001"


def test_empty_signal_set_returns_empty_payload():
    adapter = Phase11OptimizationAdapter()

    signal_set = OptimizationSignalSet()

    result = adapter.adapt(signal_set)

    assert result == {
        "skills_to_emphasize": [],
        "experience_to_emphasize": [],
        "keywords_to_emphasize": [],
        "emphasis_instructions": [],
        "grounding": [],
        "metadata": {},
    }


def test_rejects_invalid_signal_set():
    adapter = Phase11OptimizationAdapter()

    with pytest.raises(
        TypeError,
        match="OptimizationSignalSet",
    ):
        adapter.adapt([])


def test_rejects_invalid_signal_inside_set():
    adapter = Phase11OptimizationAdapter()

    signal_set = OptimizationSignalSet()

    signal_set.signals.append("invalid")

    with pytest.raises(
        TypeError,
        match="OptimizationSignal instances",
    ):
        adapter.adapt(signal_set)