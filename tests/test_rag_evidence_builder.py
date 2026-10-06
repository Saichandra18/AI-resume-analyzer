import pytest

from app.rag.grounding.evidence import EvidenceBuilder
from app.rag.models import RetrievedChunk, GroundedEvidence


def make_chunk(
    chunk_id="doc1:0",
    document_id="doc1",
    text="Python and Flask experience",
    score=0.9,
    metadata=None,
):
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id=document_id,
        text=text,
        score=score,
        metadata=metadata or {},
    )


def test_builds_grounded_evidence():
    builder = EvidenceBuilder()

    result = builder.build([
        make_chunk(),
    ])

    assert len(result) == 1
    assert isinstance(
        result[0],
        GroundedEvidence,
    )


def test_preserves_chunk_text():
    builder = EvidenceBuilder()

    result = builder.build([
        make_chunk(
            text="Built REST APIs with Flask",
        ),
    ])

    assert result[0].text == (
        "Built REST APIs with Flask"
    )

    assert result[0].claim == (
        "Built REST APIs with Flask"
    )


def test_preserves_source_chunk_id():
    builder = EvidenceBuilder()

    result = builder.build([
        make_chunk(
            chunk_id="resume:experience:3",
        ),
    ])

    assert result[0].source_chunk_ids == [
        "resume:experience:3",
    ]


def test_preserves_document_id():
    builder = EvidenceBuilder()

    result = builder.build([
        make_chunk(
            document_id="resume",
        ),
    ])

    assert result[0].metadata["document_id"] == "resume"


def test_preserves_retrieval_score():
    builder = EvidenceBuilder()

    result = builder.build([
        make_chunk(
            score=0.87,
        ),
    ])

    assert result[0].confidence == 0.87
    assert result[0].metadata[
        "retrieval_score"
    ] == 0.87


def test_preserves_existing_metadata():
    builder = EvidenceBuilder()

    result = builder.build([
        make_chunk(
            metadata={
                "section": "experience",
                "source": "resume",
            },
        ),
    ])

    assert result[0].metadata["section"] == (
        "experience"
    )

    assert result[0].metadata["source"] == (
        "resume"
    )


def test_rejects_invalid_input():
    builder = EvidenceBuilder()

    with pytest.raises(TypeError):
        builder.build("invalid")


def test_rejects_invalid_chunk():
    builder = EvidenceBuilder()

    with pytest.raises(TypeError):
        builder.build([
            "invalid",
        ])