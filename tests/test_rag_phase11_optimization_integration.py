"""Integration tests for RAG signals flowing into Phase 11 optimization."""

from app.rag.optimization.signals import (
    OptimizationSignal,
    OptimizationSignalSet,
)
from app.rag.optimization.phase11_adapter import (
    Phase11OptimizationAdapter,
)


def _signal(signal_type, value):
    """Create a valid optimization signal."""

    return OptimizationSignal(
        signal_type=signal_type,
        value=value,
    )


def _signal_set(*signals):
    """Create a valid optimization signal set."""

    return OptimizationSignalSet(
        signals=list(signals)
    )


def test_skill_signal_maps_to_phase11_payload():
    adapter = Phase11OptimizationAdapter()

    signals = _signal_set(
        _signal("skill", "Python")
    )

    payload = adapter.adapt(signals)

    assert "Python" in payload["skills_to_emphasize"]


def test_experience_signal_maps_to_phase11_payload():
    adapter = Phase11OptimizationAdapter()

    signals = _signal_set(
        _signal("experience", "machine learning")
    )

    payload = adapter.adapt(signals)

    assert "machine learning" in payload["experience_to_emphasize"]


def test_keyword_signal_maps_to_phase11_payload():
    adapter = Phase11OptimizationAdapter()

    signals = _signal_set(
        _signal("keyword", "PySpark")
    )

    payload = adapter.adapt(signals)

    assert "PySpark" in payload["keywords_to_emphasize"]


def test_emphasis_signal_maps_to_phase11_payload():
    adapter = Phase11OptimizationAdapter()

    signals = _signal_set(
        _signal(
            "emphasis",
            "Highlight data engineering experience.",
        )
    )

    payload = adapter.adapt(signals)

    assert (
        "Highlight data engineering experience."
        in payload["emphasis_instructions"]
    )


def test_multiple_signal_types_are_preserved():
    adapter = Phase11OptimizationAdapter()

    signals = _signal_set(
        _signal("skill", "Python"),
        _signal("experience", "Machine Learning"),
        _signal("keyword", "PySpark"),
        _signal(
            "emphasis",
            "Emphasize analytical projects.",
        ),
    )

    payload = adapter.adapt(signals)

    assert "Python" in payload["skills_to_emphasize"]
    assert "Machine Learning" in payload["experience_to_emphasize"]
    assert "PySpark" in payload["keywords_to_emphasize"]
    assert (
        "Emphasize analytical projects."
        in payload["emphasis_instructions"]
    )


def test_empty_signals_produce_empty_phase11_fields():
    adapter = Phase11OptimizationAdapter()

    signals = OptimizationSignalSet(
        signals=[]
    )

    payload = adapter.adapt(signals)

    assert payload["skills_to_emphasize"] == []
    assert payload["experience_to_emphasize"] == []
    assert payload["keywords_to_emphasize"] == []
    assert payload["emphasis_instructions"] == []