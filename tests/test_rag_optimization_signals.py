import pytest

from app.rag.optimization.signals import (
    OptimizationSignal,
    OptimizationSignalSet,
)


def test_creates_signal():
    signal = OptimizationSignal(
        signal_type="skill",
        value="Python",
        evidence_id="evidence:0",
        source_chunk_ids=[
            "resume:experience:0"
        ],
        confidence=0.9,
    )

    assert signal.signal_type == "skill"
    assert signal.value == "Python"
    assert signal.evidence_id == "evidence:0"


def test_normalizes_value():
    signal = OptimizationSignal(
        signal_type="skill",
        value="  Python  ",
    )

    assert signal.value == "Python"


def test_preserves_source_chunks():
    signal = OptimizationSignal(
        signal_type="experience",
        value="REST API development",
        source_chunk_ids=[
            "resume:experience:0"
        ],
    )

    assert signal.source_chunk_ids == [
        "resume:experience:0"
    ]


def test_defaults_optional_values():
    signal = OptimizationSignal(
        signal_type="keyword",
        value="Flask",
    )

    assert signal.evidence_id is None
    assert signal.source_chunk_ids == []
    assert signal.confidence == 0.0
    assert signal.metadata == {}


def test_to_dict():
    signal = OptimizationSignal(
        signal_type="skill",
        value="Python",
        evidence_id="evidence:0",
        confidence=0.8,
        metadata={
            "section": "skills"
        },
    )

    data = signal.to_dict()

    assert data["signal_type"] == "skill"
    assert data["value"] == "Python"
    assert data["evidence_id"] == "evidence:0"
    assert data["confidence"] == 0.8
    assert data["metadata"]["section"] == "skills"


def test_from_dict():
    data = {
        "signal_type": "skill",
        "value": "Python",
        "evidence_id": "evidence:0",
        "source_chunk_ids": [
            "resume:experience:0"
        ],
        "confidence": 0.9,
        "metadata": {
            "section": "experience"
        },
    }

    signal = OptimizationSignal.from_dict(
        data
    )

    assert signal.signal_type == "skill"
    assert signal.value == "Python"
    assert signal.evidence_id == "evidence:0"


def test_signal_round_trip():
    original = OptimizationSignal(
        signal_type="experience",
        value="REST API development",
        evidence_id="evidence:0",
        source_chunk_ids=[
            "resume:experience:0"
        ],
        confidence=0.9,
        metadata={
            "source": "rag"
        },
    )

    restored = OptimizationSignal.from_dict(
        original.to_dict()
    )

    assert restored.to_dict() == (
        original.to_dict()
    )


def test_rejects_invalid_signal_type():
    with pytest.raises(ValueError):
        OptimizationSignal(
            signal_type="invalid",
            value="Python",
        )


def test_rejects_empty_value():
    with pytest.raises(ValueError):
        OptimizationSignal(
            signal_type="skill",
            value="   ",
        )


def test_rejects_invalid_value():
    with pytest.raises(TypeError):
        OptimizationSignal(
            signal_type="skill",
            value=123,
        )


def test_rejects_invalid_confidence():
    with pytest.raises(ValueError):
        OptimizationSignal(
            signal_type="skill",
            value="Python",
            confidence=1.5,
        )


def test_creates_signal_set():
    signal = OptimizationSignal(
        signal_type="skill",
        value="Python",
    )

    signal_set = OptimizationSignalSet(
        signals=[signal]
    )

    assert len(signal_set.signals) == 1
    assert signal_set.signals[0] is signal


def test_signal_set_accepts_dictionaries():
    signal_set = OptimizationSignalSet(
        signals=[
            {
                "signal_type": "skill",
                "value": "Python",
            }
        ]
    )

    assert len(signal_set.signals) == 1
    assert signal_set.signals[0].value == "Python"


def test_signal_set_round_trip():
    signal_set = OptimizationSignalSet(
        signals=[
            OptimizationSignal(
                signal_type="skill",
                value="Python",
            ),
            OptimizationSignal(
                signal_type="experience",
                value="Flask development",
            ),
        ],
        metadata={
            "source": "rag"
        },
    )

    restored = OptimizationSignalSet.from_dict(
        signal_set.to_dict()
    )

    assert restored.to_dict() == (
        signal_set.to_dict()
    )


def test_signal_set_defaults_empty():
    signal_set = OptimizationSignalSet()

    assert signal_set.signals == []
    assert signal_set.metadata == {}


def test_signal_set_rejects_invalid_signals():
    with pytest.raises(TypeError):
        OptimizationSignalSet(
            signals=["invalid"]
        )


def test_signal_set_rejects_invalid_metadata():
    with pytest.raises(TypeError):
        OptimizationSignalSet(
            metadata="invalid"
        )