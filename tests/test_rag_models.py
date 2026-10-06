"""Tests for RAG core models."""

import pytest

from app.rag.models import (
    DocumentChunk,
    EmbeddingRecord,
    GroundedEvidence,
    KnowledgeDocument,
    RAGContext,
    RetrievedChunk,
    RetrievalQuery,
)


def test_knowledge_document_round_trip():
    document = KnowledgeDocument(
        document_id="doc-1",
        content="Machine learning knowledge.",
        title="ML Guide",
        source="internal",
        category="machine_learning",
        metadata={"role": "ml_engineer"},
    )

    restored = KnowledgeDocument.from_dict(
        document.to_dict()
    )

    assert restored.to_dict() == document.to_dict()


def test_knowledge_document_requires_id():
    with pytest.raises(ValueError):
        KnowledgeDocument(
            document_id="",
            content="content",
        )


def test_document_chunk_round_trip():
    chunk = DocumentChunk(
        chunk_id="chunk-1",
        document_id="doc-1",
        text="Python is commonly used.",
        chunk_index=2,
        metadata={"topic": "skills"},
    )

    restored = DocumentChunk.from_dict(
        chunk.to_dict()
    )

    assert restored.to_dict() == chunk.to_dict()


def test_document_chunk_rejects_negative_index():
    with pytest.raises(ValueError):
        DocumentChunk(
            chunk_id="chunk-1",
            document_id="doc-1",
            text="content",
            chunk_index=-1,
        )


def test_embedding_record_infers_dimensions():
    record = EmbeddingRecord(
        chunk_id="chunk-1",
        vector=[0.1, 0.2, 0.3],
        model="test-model",
    )

    assert record.dimensions == 3


def test_embedding_record_validates_dimensions():
    with pytest.raises(ValueError):
        EmbeddingRecord(
            chunk_id="chunk-1",
            vector=[0.1, 0.2],
            dimensions=3,
        )


def test_retrieval_query_defaults():
    query = RetrievalQuery(
        query="machine learning engineer",
    )

    assert query.top_k == 5
    assert query.query_type == "general"
    assert query.filters == {}


def test_retrieval_query_rejects_empty_query():
    with pytest.raises(ValueError):
        RetrievalQuery(query="   ")


def test_retrieval_query_rejects_invalid_top_k():
    with pytest.raises(ValueError):
        RetrievalQuery(
            query="python",
            top_k=0,
        )


def test_retrieved_chunk_round_trip():
    chunk = RetrievedChunk(
        chunk_id="chunk-1",
        document_id="doc-1",
        text="Relevant knowledge.",
        score=0.87,
        metadata={"category": "skills"},
    )

    restored = RetrievedChunk.from_dict(
        chunk.to_dict()
    )

    assert restored.to_dict() == chunk.to_dict()


def test_grounded_evidence_round_trip():
    evidence = GroundedEvidence(
        evidence_id="evidence-1",
        text="Python is relevant.",
        source_chunk_ids=[
            "chunk-1",
            "chunk-2",
        ],
        claim="Python is relevant to the target role.",
        confidence=0.91,
    )

    restored = GroundedEvidence.from_dict(
        evidence.to_dict()
    )

    assert restored.to_dict() == evidence.to_dict()


def test_rag_context_round_trip():
    query = RetrievalQuery(
        query="machine learning engineer",
        top_k=3,
        query_type="jd_aware",
    )

    retrieved = RetrievedChunk(
        chunk_id="chunk-1",
        document_id="doc-1",
        text="PyTorch is used for deep learning.",
        score=0.94,
    )

    evidence = GroundedEvidence(
        evidence_id="evidence-1",
        text="PyTorch is relevant.",
        source_chunk_ids=["chunk-1"],
        claim="PyTorch is relevant to the role.",
        confidence=0.9,
    )

    context = RAGContext(
        query=query,
        retrieved_chunks=[retrieved],
        evidence=[evidence],
        recommendations=[
            "Prioritize existing PyTorch experience."
        ],
        metadata={"role": "ml_engineer"},
    )

    restored = RAGContext.from_dict(
        context.to_dict()
    )

    assert restored.to_dict() == context.to_dict()


def test_rag_context_accepts_dictionary_components():
    context = RAGContext(
        query={
            "query": "python developer",
            "top_k": 2,
        },
        retrieved_chunks=[
            {
                "chunk_id": "chunk-1",
                "text": "Python experience.",
                "score": 0.8,
            }
        ],
        evidence=[
            {
                "evidence_id": "evidence-1",
                "text": "Python is relevant.",
                "source_chunk_ids": ["chunk-1"],
            }
        ],
    )

    assert context.query.query == (
        "python developer"
    )
    assert len(context.retrieved_chunks) == 1
    assert len(context.evidence) == 1


def test_models_defensively_copy_metadata():
    metadata = {
        "role": "ml_engineer",
        "topics": ["python"],
    }

    document = KnowledgeDocument(
        document_id="doc-1",
        content="content",
        metadata=metadata,
    )

    metadata["role"] = "changed"
    metadata["topics"].append("kubernetes")

    assert document.metadata == {
        "role": "ml_engineer",
        "topics": ["python"],
    }


def test_rag_context_defaults_to_empty_collections():
    context = RAGContext()

    assert context.query is None
    assert context.retrieved_chunks == []
    assert context.evidence == []
    assert context.recommendations == []
    assert context.metadata == {}