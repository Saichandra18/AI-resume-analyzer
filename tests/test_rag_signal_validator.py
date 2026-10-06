import pytest

from app.rag.models import GroundedEvidence, RetrievedChunk
from app.rag.optimization.signal_validator import SignalGroundingValidator
from app.rag.optimization.signals import (
    OptimizationSignal,
    OptimizationSignalSet,
)


def make_chunk(
    chunk_id="doc:0",
    text="Python and SQL experience",
    score=0.9,
):
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc",
        text=text,
        score=score,
        metadata={"document_id": "doc"},
    )


def make_evidence(
    evidence_id="evidence:0",
    text="Python and SQL experience",
    claim="Python",
    confidence=0.9,
    source_chunk_ids=None,
):
    return GroundedEvidence(
        evidence_id=evidence_id,
        text=text,
        source_chunk_ids=source_chunk_ids or ["doc:0"],
        claim=claim,
        confidence=confidence,
        metadata={"document_id": "doc"},
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


def test_accepts_fully_grounded_signal():
    validator = SignalGroundingValidator()

    assert validator.validate(
        [make_signal()],
        [make_evidence()],
        [make_chunk()],
    ) is True


def test_accepts_optimization_signal_set():
    validator = SignalGroundingValidator()

    signal_set = OptimizationSignalSet(
        signals=[make_signal()]
    )

    assert validator.validate_set(
        signal_set,
        [make_evidence()],
        [make_chunk()],
    ) is True


def test_rejects_invalid_signal_type():
    with pytest.raises(
        ValueError,
        match="Unsupported optimization signal type",
    ):
        make_signal(signal_type="unsupported")


def test_rejects_empty_signal_value():
    with pytest.raises(
        ValueError,
        match="value cannot be empty",
    ):
        make_signal(value="   ")


def test_rejects_missing_evidence_reference():
    validator = SignalGroundingValidator()

    signal = make_signal(evidence_id="missing:evidence")

    with pytest.raises(
        ValueError,
        match="Unknown evidence reference",
    ):
        validator.validate(
            [signal],
            [make_evidence()],
            [make_chunk()],
        )


def test_rejects_missing_source_chunk():
    validator = SignalGroundingValidator()

    signal = make_signal(
        source_chunk_ids=["missing:chunk"]
    )

    with pytest.raises(
        ValueError,
        match="unknown source chunks",
    ):
        validator.validate(
            [signal],
            [make_evidence()],
            [make_chunk()],
        )


def test_rejects_source_chunk_not_present_in_evidence():
    validator = SignalGroundingValidator()

    evidence = make_evidence(
        source_chunk_ids=["doc:1"]
    )

    signal = make_signal(
        source_chunk_ids=["doc:0"]
    )

    with pytest.raises(
        ValueError,
        match="do not match its evidence",
    ):
        validator.validate(
            [signal],
            [evidence],
            [make_chunk()],
        )


def test_rejects_confidence_mismatch():
    validator = SignalGroundingValidator()

    signal = make_signal(confidence=0.8)
    evidence = make_evidence(confidence=0.9)

    with pytest.raises(
        ValueError,
        match="confidence must match",
    ):
        validator.validate(
            [signal],
            [evidence],
            [make_chunk()],
        )


def test_rejects_confidence_outside_range():
    with pytest.raises(
        ValueError,
        match="confidence must be between 0.0 and 1.0",
    ):
        make_signal(confidence=1.5)


def test_rejects_unsupported_signal_term():
    class RejectLangChainDetector:
        def detect(self, recommendation, evidence):
            assert isinstance(recommendation, dict)
            assert recommendation["value"] == "LangChain"
            return ["langchain"]

    validator = SignalGroundingValidator(
        claim_detector=RejectLangChainDetector()
    )

    signal = make_signal(value="LangChain")

    evidence = make_evidence(
        text="Python and SQL experience with LangChain",
        claim="LangChain",
    )

    chunk = make_chunk(
        text="Python and SQL experience with LangChain",
    )

    with pytest.raises(
        ValueError,
        match="unsupported terms",
    ):
        validator.validate(
            [signal],
            [evidence],
            [chunk],
        )


def test_rejects_signal_value_not_supported_by_evidence():
    class NoUnsupportedTermsDetector:
        def detect(self, recommendation, evidence):
            assert isinstance(recommendation, dict)
            return []

    validator = SignalGroundingValidator(
        claim_detector=NoUnsupportedTermsDetector()
    )

    signal = make_signal(
        value="Kubernetes"
    )

    with pytest.raises(
        ValueError,
        match="not supported by referenced evidence",
    ):
        validator.validate(
            [signal],
            [make_evidence()],
            [make_chunk()],
        )


def test_rejects_document_metadata_mismatch():
    validator = SignalGroundingValidator()

    signal = make_signal(
        metadata={"document_id": "different-document"}
    )

    with pytest.raises(
        ValueError,
        match="document metadata",
    ):
        validator.validate(
            [signal],
            [make_evidence()],
            [make_chunk()],
        )


def test_rejects_non_signal_items():
    validator = SignalGroundingValidator()

    with pytest.raises(
        TypeError,
        match="OptimizationSignal instances",
    ):
        validator.validate(
            [{"signal_type": "skill"}],
            [make_evidence()],
            [make_chunk()],
        )


def test_rejects_non_evidence_items():
    validator = SignalGroundingValidator()

    with pytest.raises(
        TypeError,
        match="GroundedEvidence",
    ):
        validator.validate(
            [make_signal()],
            [{"evidence_id": "evidence:0"}],
            [make_chunk()],
        )


def test_rejects_non_chunk_items():
    validator = SignalGroundingValidator()

    with pytest.raises(
        TypeError,
        match="RetrievedChunk",
    ):
        validator.validate(
            [make_signal()],
            [make_evidence()],
            [{"chunk_id": "doc:0"}],
        )


def test_rejects_invalid_signal_set():
    validator = SignalGroundingValidator()

    with pytest.raises(
        TypeError,
        match="OptimizationSignalSet",
    ):
        validator.validate_set(
            [],
            [make_evidence()],
            [make_chunk()],
        )