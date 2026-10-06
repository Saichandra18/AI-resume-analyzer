"""Tests for the RAG document chunker."""

import pytest

from app.rag.ingestion.chunker import DocumentChunker


def test_chunk_empty_text_returns_empty_list():
    chunker = DocumentChunker()

    assert chunker.chunk("") == []


def test_chunk_none_raises_error():
    chunker = DocumentChunker()

    with pytest.raises(ValueError):
        chunker.chunk(None)


def test_chunk_non_string_raises_error():
    chunker = DocumentChunker()

    with pytest.raises(TypeError):
        chunker.chunk(["Python"])


def test_chunk_requires_document_id():
    chunker = DocumentChunker()

    with pytest.raises(ValueError):
        chunker.chunk(
            "Python",
            document_id="",
        )


def test_chunk_creates_document_chunks():
    chunker = DocumentChunker(
        chunk_size=100,
        overlap=20,
    )

    chunks = chunker.chunk(
        "Python is useful.\nFlask is a web framework.",
        document_id="doc-1",
    )

    assert len(chunks) == 1
    assert chunks[0].chunk_id == "doc-1:0"
    assert chunks[0].document_id == "doc-1"
    assert "Python" in chunks[0].text
    assert "Flask" in chunks[0].text


def test_chunk_splits_large_document():
    chunker = DocumentChunker(
        chunk_size=30,
        overlap=5,
    )

    text = (
        "Python is a programming language.\n"
        "Flask is a web framework.\n"
        "RAG improves contextual retrieval."
    )

    chunks = chunker.chunk(
        text,
        document_id="doc-2",
    )

    assert len(chunks) >= 2

    assert chunks[0].chunk_id == "doc-2:0"
    assert chunks[1].chunk_id == "doc-2:1"


def test_chunk_preserves_metadata():
    chunker = DocumentChunker(
        chunk_size=100,
        overlap=10,
    )

    metadata = {
        "source": "knowledge-base",
        "topic": "python",
    }

    chunks = chunker.chunk(
        "Python is useful.",
        document_id="doc-3",
        metadata=metadata,
    )

    assert chunks[0].metadata["source"] == "knowledge-base"
    assert chunks[0].metadata["topic"] == "python"
    assert chunks[0].metadata["document_id"] == "doc-3"
    assert chunks[0].metadata["chunk_index"] == 0


def test_chunk_copies_metadata():
    chunker = DocumentChunker()

    metadata = {
        "topic": "python",
    }

    chunks = chunker.chunk(
        "Python is useful.",
        document_id="doc-4",
        metadata=metadata,
    )

    metadata["topic"] = "changed"

    assert chunks[0].metadata["topic"] == "python"


def test_chunk_validates_constructor_values():
    with pytest.raises(TypeError):
        DocumentChunker(chunk_size="100")

    with pytest.raises(TypeError):
        DocumentChunker(overlap="20")

    with pytest.raises(ValueError):
        DocumentChunker(chunk_size=0)

    with pytest.raises(ValueError):
        DocumentChunker(overlap=-1)

    with pytest.raises(ValueError):
        DocumentChunker(
            chunk_size=100,
            overlap=100,
        )


def test_chunk_validates_metadata():
    chunker = DocumentChunker()

    with pytest.raises(TypeError):
        chunker.chunk(
            "Python",
            metadata=["invalid"],
        )


def test_chunk_validates_document_id_type():
    chunker = DocumentChunker()

    with pytest.raises(TypeError):
        chunker.chunk(
            "Python",
            document_id=123,
        )

def test_chunk_metadata_contains_document_id():
    chunker = DocumentChunker()

    chunks = chunker.chunk(
        "Python is useful.",
        document_id="doc-5",
    )

    assert chunks[0].metadata["document_id"] == "doc-5"


def test_chunk_metadata_contains_chunk_index():
    chunker = DocumentChunker(
        chunk_size=30,
        overlap=5,
    )

    text = (
        "Python is a programming language.\n"
        "Flask is a web framework."
    )

    chunks = chunker.chunk(
        text,
        document_id="doc-6",
    )

    assert chunks[0].metadata["chunk_index"] == 0

    if len(chunks) > 1:
        assert chunks[1].metadata["chunk_index"] == 1


def test_explicit_metadata_is_preserved():
    chunker = DocumentChunker()

    metadata = {
        "source": "official-docs",
        "category": "technology",
    }

    chunks = chunker.chunk(
        "Python is useful.",
        document_id="doc-7",
        metadata=metadata,
    )

    assert chunks[0].metadata["source"] == "official-docs"
    assert chunks[0].metadata["category"] == "technology"


def test_generated_metadata_does_not_override_explicit_metadata():
    chunker = DocumentChunker()

    metadata = {
        "document_id": "custom-document",
        "chunk_index": 99,
    }

    chunks = chunker.chunk(
        "Python is useful.",
        document_id="doc-8",
        metadata=metadata,
    )

    assert chunks[0].metadata["document_id"] == (
        "custom-document"
    )
    assert chunks[0].metadata["chunk_index"] == 99