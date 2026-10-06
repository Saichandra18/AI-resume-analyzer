import pytest

from app.rag.grounding.context_builder import RAGContextBuilder
from app.rag.models import (
    GroundedEvidence,
    RAGContext,
    RetrievedChunk,
    RetrievalQuery,
)


def make_chunk(
    chunk_id="doc1:0",
    text="Python Flask experience",
):
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc1",
        text=text,
        score=0.9,
        metadata={"section": "experience"},
    )


def make_evidence(
    evidence_id="evidence:0",
    text="Python Flask experience",
):
    return GroundedEvidence(
        evidence_id=evidence_id,
        text=text,
        source_chunk_ids=["doc1:0"],
        claim=text,
        confidence=0.9,
        metadata={"section": "experience"},
    )


def test_builds_rag_context():
    builder = RAGContextBuilder()

    context = builder.build(
        retrieved_chunks=[make_chunk()],
        grounded_evidence=[make_evidence()],
    )

    assert isinstance(context, RAGContext)


def test_preserves_retrieved_chunks():
    builder = RAGContextBuilder()

    chunks = [make_chunk()]

    context = builder.build(
        retrieved_chunks=chunks,
        grounded_evidence=[],
    )

    assert context.retrieved_chunks == chunks


def test_preserves_grounded_evidence():
    builder = RAGContextBuilder()

    evidence = [make_evidence()]

    context = builder.build(
        retrieved_chunks=[],
        grounded_evidence=evidence,
    )

    assert context.evidence == evidence


def test_preserves_query():
    builder = RAGContextBuilder()

    query = RetrievalQuery(
        query="Python Flask",
        top_k=5,
    )

    context = builder.build(
        retrieved_chunks=[],
        grounded_evidence=[],
        query=query,
    )

    assert context.query is query

def test_preserves_metadata():
    builder = RAGContextBuilder()

    metadata = {
        "source": "resume",
        "query_type": "jd",
    }

    context = builder.build(
        retrieved_chunks=[],
        grounded_evidence=[],
        metadata=metadata,
    )

    assert context.metadata == metadata


def test_defaults_optional_values():
    builder = RAGContextBuilder()

    context = builder.build(
        retrieved_chunks=[],
        grounded_evidence=[],
    )

    assert context.query is None
    assert context.metadata == {}


def test_rejects_invalid_retrieved_chunks():
    builder = RAGContextBuilder()

    with pytest.raises(TypeError):
        builder.build(
            retrieved_chunks=["invalid"],
            grounded_evidence=[],
        )


def test_rejects_invalid_evidence():
    builder = RAGContextBuilder()

    with pytest.raises(TypeError):
        builder.build(
            retrieved_chunks=[],
            grounded_evidence=["invalid"],
        )