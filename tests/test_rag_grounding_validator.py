import pytest

from app.rag.grounding.validator import GroundingValidator
from app.rag.models import GroundedEvidence, RetrievedChunk


def make_chunk(
    chunk_id="doc1:0",
    text="Python Flask experience",
):
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc1",
        text=text,
        score=0.9,
        metadata={},
    )


def make_evidence(
    evidence_id="evidence:0",
    text="Python Flask experience",
    claim="Python Flask experience",
    source_chunk_ids=None,
    confidence=0.9,
):
    return GroundedEvidence(
        evidence_id=evidence_id,
        text=text,
        source_chunk_ids=(
            ["doc1:0"]
            if source_chunk_ids is None
            else source_chunk_ids
        ),
        claim=claim,
        confidence=confidence,
        metadata={},
    )


def test_valid_evidence_passes():
    validator = GroundingValidator()

    assert validator.validate(
        [make_evidence()],
        [make_chunk()],
    ) is True


def test_evidence_must_reference_retrieved_chunk():
    validator = GroundingValidator()

    evidence = make_evidence(
        source_chunk_ids=["missing:0"],
    )

    with pytest.raises(ValueError):
        validator.validate(
            [evidence],
            [make_chunk()],
        )


def test_evidence_requires_source_chunk():
    validator = GroundingValidator()

    evidence = make_evidence(
        source_chunk_ids=[],
    )

    with pytest.raises(ValueError):
        validator.validate(
            [evidence],
            [make_chunk()],
        )


def test_evidence_requires_text():
    validator = GroundingValidator()

    evidence = make_evidence(
        text="   ",
        claim="something",
    )

    with pytest.raises(ValueError):
        validator.validate(
            [evidence],
            [make_chunk()],
        )


def test_evidence_requires_claim():
    validator = GroundingValidator()

    evidence = make_evidence(
        claim="   ",
    )

    with pytest.raises(ValueError):
        validator.validate(
            [evidence],
            [make_chunk()],
        )


def test_claim_must_be_traceable_to_text():
    validator = GroundingValidator()

    evidence = make_evidence(
        text="Python Flask experience",
        claim="React experience",
    )

    with pytest.raises(ValueError):
        validator.validate(
            [evidence],
            [make_chunk()],
        )


def test_confidence_must_not_exceed_one():
    validator = GroundingValidator()

    evidence = make_evidence(
        confidence=1.1,
    )

    with pytest.raises(ValueError):
        validator.validate(
            [evidence],
            [make_chunk()],
        )


def test_confidence_must_not_be_negative():
    validator = GroundingValidator()

    evidence = make_evidence(
        confidence=-0.1,
    )

    with pytest.raises(ValueError):
        validator.validate(
            [evidence],
            [make_chunk()],
        )


def test_rejects_invalid_evidence_collection():
    validator = GroundingValidator()

    with pytest.raises(TypeError):
        validator.validate(
            ["invalid"],
            [make_chunk()],
        )


def test_rejects_invalid_retrieved_chunks():
    validator = GroundingValidator()

    with pytest.raises(TypeError):
        validator.validate(
            [make_evidence()],
            ["invalid"],
        )