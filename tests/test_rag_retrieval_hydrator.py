"""Tests for retrieval result hydration."""

import pytest

from app.rag.models import DocumentChunk, RetrievedChunk
from app.rag.retrieval.hydrator import RetrievalHydrator
from app.rag.vectorstore.registry import ChunkRegistry


def make_registry():
    registry = ChunkRegistry()

    registry.add(
        [
            DocumentChunk(
                chunk_id="chunk-1",
                document_id="doc-1",
                text="Python backend development experience.",
                chunk_index=0,
                metadata={
                    "section": "experience",
                    "source": "resume.txt",
                },
            ),
            DocumentChunk(
                chunk_id="chunk-2",
                document_id="doc-1",
                text="Built REST APIs using Flask.",
                chunk_index=1,
                metadata={
                    "section": "projects",
                    "source": "resume.txt",
                },
            ),
        ]
    )

    return registry


def test_hydrates_retrieved_chunk_text():
    registry = make_registry()
    hydrator = RetrievalHydrator(registry)

    retrieved = [
        RetrievedChunk(
            chunk_id="chunk-1",
            text="",
            score=0.95,
        )
    ]

    result = hydrator.hydrate(retrieved)

    assert len(result) == 1
    assert result[0].chunk_id == "chunk-1"
    assert result[0].text == (
        "Python backend development experience."
    )


def test_hydrates_document_id():
    registry = make_registry()
    hydrator = RetrievalHydrator(registry)

    retrieved = [
        RetrievedChunk(
            chunk_id="chunk-1",
            text="",
            score=0.9,
        )
    ]

    result = hydrator.hydrate(retrieved)

    assert result[0].document_id == "doc-1"


def test_hydrates_metadata():
    registry = make_registry()
    hydrator = RetrievalHydrator(registry)

    retrieved = [
        RetrievedChunk(
            chunk_id="chunk-2",
            text="",
            score=0.8,
        )
    ]

    result = hydrator.hydrate(retrieved)

    assert result[0].metadata == {
        "section": "projects",
        "source": "resume.txt",
    }


def test_preserves_similarity_score():
    registry = make_registry()
    hydrator = RetrievalHydrator(registry)

    retrieved = [
        RetrievedChunk(
            chunk_id="chunk-1",
            text="",
            score=0.8765,
        )
    ]

    result = hydrator.hydrate(retrieved)

    assert result[0].score == pytest.approx(0.8765)


def test_hydrates_multiple_chunks():
    registry = make_registry()
    hydrator = RetrievalHydrator(registry)

    retrieved = [
        RetrievedChunk(
            chunk_id="chunk-1",
            text="",
            score=0.95,
        ),
        RetrievedChunk(
            chunk_id="chunk-2",
            text="",
            score=0.85,
        ),
    ]

    result = hydrator.hydrate(retrieved)

    assert len(result) == 2
    assert result[0].text == (
        "Python backend development experience."
    )
    assert result[1].text == (
        "Built REST APIs using Flask."
    )


def test_preserves_retrieval_order():
    registry = make_registry()
    hydrator = RetrievalHydrator(registry)

    retrieved = [
        RetrievedChunk(
            chunk_id="chunk-2",
            text="",
            score=0.95,
        ),
        RetrievedChunk(
            chunk_id="chunk-1",
            text="",
            score=0.85,
        ),
    ]

    result = hydrator.hydrate(retrieved)

    assert [chunk.chunk_id for chunk in result] == [
        "chunk-2",
        "chunk-1",
    ]


def test_missing_chunk_is_skipped():
    registry = make_registry()
    hydrator = RetrievalHydrator(registry)

    retrieved = [
        RetrievedChunk(
            chunk_id="missing",
            text="",
            score=0.95,
        ),
        RetrievedChunk(
            chunk_id="chunk-1",
            text="",
            score=0.85,
        ),
    ]

    result = hydrator.hydrate(retrieved)

    assert len(result) == 1
    assert result[0].chunk_id == "chunk-1"


def test_empty_results_return_empty_list():
    registry = make_registry()
    hydrator = RetrievalHydrator(registry)

    assert hydrator.hydrate([]) == []


def test_requires_registry():
    with pytest.raises(ValueError):
        RetrievalHydrator(None)


def test_requires_registry_get_method():
    class InvalidRegistry:
        pass

    with pytest.raises(TypeError):
        RetrievalHydrator(InvalidRegistry())


def test_requires_list_or_tuple():
    registry = make_registry()
    hydrator = RetrievalHydrator(registry)

    with pytest.raises(TypeError):
        hydrator.hydrate(None)


def test_requires_retrieved_chunk_instances():
    registry = make_registry()
    hydrator = RetrievalHydrator(registry)

    with pytest.raises(TypeError):
        hydrator.hydrate(["chunk-1"])