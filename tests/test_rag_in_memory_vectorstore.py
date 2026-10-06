"""Tests for the in-memory RAG vector store."""

import pytest

from app.rag.models import EmbeddingRecord
from app.rag.vectorstore.in_memory import (
    InMemoryVectorStore,
)


def record(
    chunk_id,
    vector,
    text="",
    metadata=None,
):
    metadata = dict(metadata or {})
    metadata["text"] = text

    return EmbeddingRecord(
        chunk_id=chunk_id,
        vector=vector,
        metadata=metadata,
    )


def test_store_starts_empty():
    store = InMemoryVectorStore()

    assert store.count() == 0


def test_add_records():
    store = InMemoryVectorStore()

    store.add([
        record(
            "doc:0",
            [1.0, 0.0],
        ),
        record(
            "doc:1",
            [0.0, 1.0],
        ),
    ])

    assert store.count() == 2


def test_add_replaces_same_chunk_id():
    store = InMemoryVectorStore()

    store.add([
        record(
            "doc:0",
            [1.0, 0.0],
        )
    ])

    store.add([
        record(
            "doc:0",
            [0.0, 1.0],
        )
    ])

    assert store.count() == 1


def test_search_returns_most_similar_first():
    store = InMemoryVectorStore()

    store.add([
        record(
            "doc:0",
            [1.0, 0.0],
            text="Python",
        ),
        record(
            "doc:1",
            [0.0, 1.0],
            text="Java",
        ),
    ])

    results = store.search(
        [1.0, 0.0],
    )

    assert len(results) == 2
    assert results[0].chunk_id == "doc:0"
    assert results[0].score == pytest.approx(1.0)
    assert results[1].chunk_id == "doc:1"
    assert results[1].score == pytest.approx(0.0)


def test_search_respects_top_k():
    store = InMemoryVectorStore()

    store.add([
        record("doc:0", [1.0, 0.0]),
        record("doc:1", [0.9, 0.1]),
        record("doc:2", [0.0, 1.0]),
    ])

    results = store.search(
        [1.0, 0.0],
        top_k=2,
    )

    assert len(results) == 2
    assert [
        result.chunk_id
        for result in results
    ] == [
        "doc:0",
        "doc:1",
    ]


def test_search_preserves_text_and_metadata():
    store = InMemoryVectorStore()

    store.add([
        record(
            "doc:0",
            [1.0, 0.0],
            text="Python is useful.",
            metadata={
                "topic": "python",
            },
        )
    ])

    results = store.search(
        [1.0, 0.0],
    )

    assert results[0].text == (
        "Python is useful."
    )

    assert results[0].metadata["topic"] == (
        "python"
    )


def test_search_supports_metadata_filters():
    store = InMemoryVectorStore()

    store.add([
        record(
            "doc:0",
            [1.0, 0.0],
            metadata={
                "category": "python",
            },
        ),
        record(
            "doc:1",
            [1.0, 0.0],
            metadata={
                "category": "java",
            },
        ),
    ])

    results = store.search(
        [1.0, 0.0],
        filters={
            "category": "python",
        },
    )

    assert len(results) == 1
    assert results[0].chunk_id == "doc:0"


def test_delete_records():
    store = InMemoryVectorStore()

    store.add([
        record("doc:0", [1.0, 0.0]),
        record("doc:1", [0.0, 1.0]),
    ])

    store.delete(["doc:0"])

    assert store.count() == 1

    results = store.search(
        [1.0, 0.0],
    )

    assert results[0].chunk_id == "doc:1"


def test_delete_missing_id_is_safe():
    store = InMemoryVectorStore()

    store.delete(["missing"])

    assert store.count() == 0


def test_add_requires_sequence():
    store = InMemoryVectorStore()

    with pytest.raises(TypeError):
        store.add("invalid")


def test_add_requires_embedding_records():
    store = InMemoryVectorStore()

    with pytest.raises(TypeError):
        store.add(["invalid"])


def test_search_validates_top_k():
    store = InMemoryVectorStore()

    with pytest.raises(TypeError):
        store.search(
            [1.0],
            top_k="5",
        )

    with pytest.raises(ValueError):
        store.search(
            [1.0],
            top_k=0,
        )


def test_search_validates_filters():
    store = InMemoryVectorStore()

    with pytest.raises(TypeError):
        store.search(
            [1.0],
            filters=["invalid"],
        )


def test_search_rejects_dimension_mismatch():
    store = InMemoryVectorStore()

    store.add([
        record(
            "doc:0",
            [1.0, 0.0],
        )
    ])

    with pytest.raises(ValueError):
        store.search(
            [1.0, 0.0, 0.0],
        )


def test_search_rejects_invalid_query_vector():
    store = InMemoryVectorStore()

    with pytest.raises(TypeError):
        store.search("invalid")

    with pytest.raises(ValueError):
        store.search([])


def test_delete_requires_sequence():
    store = InMemoryVectorStore()

    with pytest.raises(TypeError):
        store.delete("doc:0")

def test_search_returns_original_document_chunk():
    from app.rag.models import DocumentChunk
    from app.rag.vectorstore.registry import ChunkRegistry

    registry = ChunkRegistry()

    chunk = DocumentChunk(
        chunk_id="doc1:0",
        document_id="doc1",
        text="Python Flask developer",
        metadata={"section": "experience"},
    )

    registry.add([chunk])

    store = InMemoryVectorStore(chunk_registry=registry)

    record = EmbeddingRecord(
        chunk_id="doc1:0",
        vector=[1.0, 0.0],
    )

    store.add([record])

    results = store.search([1.0, 0.0], top_k=1)

    assert len(results) == 1
    assert results[0].chunk_id == "doc1:0"
    assert results[0].document_id == "doc1"
    assert results[0].text == "Python Flask developer"
    assert results[0].metadata["section"] == "experience"

def test_search_filters_by_metadata():
    store = InMemoryVectorStore()

    store.add([
        EmbeddingRecord(
            chunk_id="doc1:0",
            vector=[1.0, 0.0],
            metadata={"section": "skills"},
        ),
        EmbeddingRecord(
            chunk_id="doc1:1",
            vector=[0.9, 0.1],
            metadata={"section": "experience"},
        ),
    ])

    results = store.search(
        [1.0, 0.0],
        filters={"section": "skills"},
    )

    assert len(results) == 1
    assert results[0].chunk_id == "doc1:0"


def test_search_filters_multiple_metadata_fields():
    store = InMemoryVectorStore()

    store.add([
        EmbeddingRecord(
            chunk_id="doc1:0",
            vector=[1.0, 0.0],
            metadata={
                "section": "skills",
                "source": "resume",
            },
        ),
        EmbeddingRecord(
            chunk_id="doc1:1",
            vector=[0.9, 0.1],
            metadata={
                "section": "skills",
                "source": "job_description",
            },
        ),
    ])

    results = store.search(
        [1.0, 0.0],
        filters={
            "section": "skills",
            "source": "resume",
        },
    )

    assert len(results) == 1
    assert results[0].chunk_id == "doc1:0"


def test_search_returns_no_results_when_metadata_does_not_match():
    store = InMemoryVectorStore()

    store.add([
        EmbeddingRecord(
            chunk_id="doc1:0",
            vector=[1.0, 0.0],
            metadata={"section": "skills"},
        ),
    ])

    results = store.search(
        [1.0, 0.0],
        filters={"section": "experience"},
    )

    assert results == []


def test_search_rejects_non_dictionary_filters():
    store = InMemoryVectorStore()

    with pytest.raises(TypeError):
        store.search(
            [1.0, 0.0],
            filters=["skills"],
        )