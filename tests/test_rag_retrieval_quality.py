import pytest

from app.rag.models import (
    DocumentChunk,
    EmbeddingRecord,
    RetrievalQuery,
)
from app.rag.retrieval.service import RetrievalService
from app.rag.vectorstore.in_memory import InMemoryVectorStore


class FakeEmbeddingProvider:
    """Deterministic embeddings for retrieval-quality tests."""

    def __init__(self, vectors):
        self.vectors = vectors

    def generate_embedding(self, text):
        return list(self.vectors[text])

    def generate_embeddings(self, texts):
        return [
            list(self.vectors[text])
            for text in texts
        ]


def make_chunk(chunk_id, text, metadata=None):
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="knowledge-doc",
        text=text,
        metadata=metadata or {},
    )


def build_retrieval_service():
    vectors = {
        "python": [1.0, 0.0, 0.0],
        "flask": [0.9, 0.1, 0.0],
        "react": [0.0, 1.0, 0.0],
        "database": [0.0, 0.9, 0.1],
        "unrelated": [0.0, 0.0, 1.0],
    }

    provider = FakeEmbeddingProvider(vectors)
    store = InMemoryVectorStore()


    chunks = [
        make_chunk(
            "python-1",
            "python",
            {"category": "backend"},
        ),
        make_chunk(
            "flask-1",
            "flask",
            {"category": "backend"},
        ),
        make_chunk(
            "react-1",
            "react",
            {"category": "frontend"},
        ),
        make_chunk(
            "database-1",
            "database",
            {"category": "data"},
        ),
        make_chunk(
            "unrelated-1",
            "unrelated",
            {"category": "other"},
        ),
    ]

    records = [
        EmbeddingRecord(
            chunk_id=chunk.chunk_id,
            vector=vectors[chunk.text],
            model="test-model",
            dimensions=3,
            metadata=chunk.metadata,
        )
        for chunk in chunks
    ]

    store.add(records)
    

    service = RetrievalService(
        embedding_provider=provider,
        vector_store=store,
    )

    return service


def test_relevant_chunks_rank_first():
    service = build_retrieval_service()

    query = RetrievalQuery(
        query="python",
        top_k=3,
    )

    results = service.retrieve(query)

    assert results
    assert results[0].chunk_id == "python-1"


def test_top_k_is_respected():
    service = build_retrieval_service()

    query = RetrievalQuery(
        query="python",
        top_k=2,
    )

    results = service.retrieve(query)

    assert len(results) == 2


def test_empty_store_returns_no_results():
    provider = FakeEmbeddingProvider(
        {"python": [1.0, 0.0, 0.0]}
    )

    store = InMemoryVectorStore()


    service = RetrievalService(
        embedding_provider=provider,
        vector_store=store,
    )

    query = RetrievalQuery(
        query="python",
        top_k=5,
    )

    assert service.retrieve(query) == []


def test_metadata_filter_restricts_results():
    service = build_retrieval_service()

    query = RetrievalQuery(
        query="python",
        top_k=5,
        filters={"category": "backend"},
    )

    results = service.retrieve(query)

    assert results
    assert all(
        result.metadata.get("category") == "backend"
        for result in results
    )


def test_metadata_filter_can_exclude_relevant_chunk():
    service = build_retrieval_service()

    query = RetrievalQuery(
        query="python",
        top_k=5,
        filters={"category": "frontend"},
    )

    results = service.retrieve(query)

    assert all(
        result.metadata.get("category") == "frontend"
        for result in results
    )
    assert "python-1" not in [
        result.chunk_id
        for result in results
    ]



def test_retrieval_preserves_metadata():
    service = build_retrieval_service()

    query = RetrievalQuery(
        query="python",
        top_k=1,
    )

    results = service.retrieve(query)

    assert results[0].metadata == {
        "category": "backend"
    }


def test_retrieval_is_deterministic():
    service = build_retrieval_service()

    query = RetrievalQuery(
        query="python",
        top_k=5,
    )

    first = service.retrieve(query)
    second = service.retrieve(query)

    assert [
        result.chunk_id
        for result in first
    ] == [
        result.chunk_id
        for result in second
    ]

    assert [
        result.score
        for result in first
    ] == [
        result.score
        for result in second
    ]


def test_retrieval_result_count_does_not_exceed_store_count():
    service = build_retrieval_service()

    query = RetrievalQuery(
        query="python",
        top_k=100,
    )

    results = service.retrieve(query)

    assert len(results) <= 5


def test_retrieval_results_have_scores():
    service = build_retrieval_service()

    query = RetrievalQuery(
        query="python",
        top_k=3,
    )

    results = service.retrieve(query)

    assert results
    assert all(
        isinstance(result.score, float)
        for result in results
    )


def test_retrieval_results_have_chunk_ids():
    service = build_retrieval_service()

    query = RetrievalQuery(
        query="python",
        top_k=3,
    )

    results = service.retrieve(query)

    assert results
    assert all(
        result.chunk_id
        for result in results
    )