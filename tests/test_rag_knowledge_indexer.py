import pytest

from app.rag.indexing import KnowledgeIndexer
from app.rag.models import DocumentChunk


class FakeEmbeddingProvider:
    def generate_embeddings(self, texts):
        return [[float(index + 1), 0.0, 0.0] for index, _ in enumerate(texts)]


class FakeVectorStore:
    def __init__(self):
        self.records = []

    def add(self, records):
        self.records.extend(records)


class FakeChunkRegistry:
    def __init__(self):
        self.chunks = {}

    def add(self, chunk):
        self.chunks[chunk.chunk_id] = chunk


def make_chunk(chunk_id="chunk-1", text="Python developer"):
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc-1",
        text=text,
        metadata={"source": "resume"},
    )


def test_indexer_requires_dependencies():
    with pytest.raises(ValueError):
        KnowledgeIndexer(None, FakeVectorStore(), FakeChunkRegistry())

    with pytest.raises(ValueError):
        KnowledgeIndexer(
            FakeEmbeddingProvider(),
            None,
            FakeChunkRegistry(),
        )

    with pytest.raises(ValueError):
        KnowledgeIndexer(
            FakeEmbeddingProvider(),
            FakeVectorStore(),
            None,
        )


def test_indexer_rejects_invalid_dependencies():
    with pytest.raises(TypeError):
        KnowledgeIndexer(
            object(),
            FakeVectorStore(),
            FakeChunkRegistry(),
        )

    with pytest.raises(TypeError):
        KnowledgeIndexer(
            FakeEmbeddingProvider(),
            object(),
            FakeChunkRegistry(),
        )

    with pytest.raises(TypeError):
        KnowledgeIndexer(
            FakeEmbeddingProvider(),
            FakeVectorStore(),
            object(),
        )


def test_indexer_requires_chunks():
    indexer = KnowledgeIndexer(
        FakeEmbeddingProvider(),
        FakeVectorStore(),
        FakeChunkRegistry(),
    )

    with pytest.raises(ValueError):
        indexer.index(None)


def test_indexer_rejects_invalid_chunks():
    indexer = KnowledgeIndexer(
        FakeEmbeddingProvider(),
        FakeVectorStore(),
        FakeChunkRegistry(),
    )

    with pytest.raises(TypeError):
        indexer.index("not-a-list")


def test_empty_chunks_return_empty_result():
    indexer = KnowledgeIndexer(
        FakeEmbeddingProvider(),
        FakeVectorStore(),
        FakeChunkRegistry(),
    )

    assert indexer.index([]) == []


def test_indexer_generates_embeddings_and_stores_records():
    vector_store = FakeVectorStore()
    registry = FakeChunkRegistry()

    indexer = KnowledgeIndexer(
        FakeEmbeddingProvider(),
        vector_store,
        registry,
    )

    chunks = [
        make_chunk("chunk-1", "Python"),
        make_chunk("chunk-2", "Flask"),
    ]

    result = indexer.index(chunks)

    assert result == ["chunk-1", "chunk-2"]

    assert len(vector_store.records) == 2
    assert vector_store.records[0]["chunk_id"] == "chunk-1"
    assert vector_store.records[1]["chunk_id"] == "chunk-2"

    assert vector_store.records[0]["embedding"] == [1.0, 0.0, 0.0]
    assert vector_store.records[1]["embedding"] == [2.0, 0.0, 0.0]

    assert registry.chunks["chunk-1"].text == "Python"
    assert registry.chunks["chunk-2"].text == "Flask"


def test_indexer_preserves_chunk_metadata():
    vector_store = FakeVectorStore()
    registry = FakeChunkRegistry()

    indexer = KnowledgeIndexer(
        FakeEmbeddingProvider(),
        vector_store,
        registry,
    )

    chunk = make_chunk()
    indexer.index([chunk])

    assert vector_store.records[0]["metadata"] == {
        "source": "resume"
    }

    assert registry.chunks["chunk-1"].metadata == {
        "source": "resume"
    }


def test_indexer_does_not_modify_original_chunks():
    vector_store = FakeVectorStore()
    registry = FakeChunkRegistry()

    indexer = KnowledgeIndexer(
        FakeEmbeddingProvider(),
        vector_store,
        registry,
    )

    chunk = make_chunk()
    original_metadata = dict(chunk.metadata)

    indexer.index([chunk])

    assert chunk.metadata == original_metadata