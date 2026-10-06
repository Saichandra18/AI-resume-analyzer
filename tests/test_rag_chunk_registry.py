import pytest

from app.rag.models import DocumentChunk
from app.rag.vectorstore.registry import ChunkRegistry


def make_chunk(chunk_id="doc1:0", text="Python developer"):
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc1",
        text=text,
        metadata={"section": "skills"},
    )


def test_add_and_get_chunk():
    registry = ChunkRegistry()
    chunk = make_chunk()

    registry.add([chunk])

    assert registry.get("doc1:0") is chunk


def test_add_multiple_chunks():
    registry = ChunkRegistry()

    registry.add([
        make_chunk("doc1:0"),
        make_chunk("doc1:1", "Flask developer"),
    ])

    assert registry.count() == 2


def test_missing_chunk_returns_none():
    registry = ChunkRegistry()

    assert registry.get("missing") is None


def test_delete_chunks():
    registry = ChunkRegistry()
    registry.add([make_chunk()])

    registry.delete(["doc1:0"])

    assert registry.get("doc1:0") is None
    assert registry.count() == 0


def test_clear():
    registry = ChunkRegistry()
    registry.add([make_chunk()])

    registry.clear()

    assert registry.count() == 0


def test_rejects_invalid_chunk():
    registry = ChunkRegistry()

    with pytest.raises(TypeError):
        registry.add(["invalid"])