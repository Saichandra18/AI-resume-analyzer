"""Tests for RAG embedding generation."""

import pytest

from app.rag.embeddings.generator import EmbeddingGenerator
from app.rag.embeddings.local import LocalEmbeddingProvider
from app.rag.models import DocumentChunk, EmbeddingRecord


def create_chunk(
    chunk_id="doc-1:0",
    text="Python is useful.",
):
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc-1",
        text=text,
    )


def test_generator_requires_provider():
    with pytest.raises(ValueError):
        EmbeddingGenerator(None)


def test_generator_requires_embedding_method():
    class InvalidProvider:
        pass

    with pytest.raises(TypeError):
        EmbeddingGenerator(
            InvalidProvider()
        )


def test_generate_returns_embedding_record():
    provider = LocalEmbeddingProvider(
        dimension=16
    )

    generator = EmbeddingGenerator(provider)

    chunk = create_chunk()

    record = generator.generate(chunk)

    assert isinstance(
        record,
        EmbeddingRecord,
    )

    assert record.chunk_id == chunk.chunk_id
    assert len(record.vector) == 16


def test_generate_preserves_chunk_identity():
    provider = LocalEmbeddingProvider(
        dimension=8
    )

    generator = EmbeddingGenerator(provider)

    chunk = create_chunk(
        chunk_id="document-a:7"
    )

    record = generator.generate(chunk)

    assert record.chunk_id == "document-a:7"


def test_generate_requires_document_chunk():
    provider = LocalEmbeddingProvider(
        dimension=8
    )

    generator = EmbeddingGenerator(provider)

    with pytest.raises(TypeError):
        generator.generate("invalid")


def test_generate_batch():
    provider = LocalEmbeddingProvider(
        dimension=16
    )

    generator = EmbeddingGenerator(provider)

    chunks = [
        create_chunk(
            chunk_id="doc-1:0",
            text="Python",
        ),
        create_chunk(
            chunk_id="doc-1:1",
            text="Flask",
        ),
        create_chunk(
            chunk_id="doc-1:2",
            text="RAG",
        ),
    ]

    records = generator.generate_batch(
        chunks
    )

    assert len(records) == 3

    assert [
        record.chunk_id
        for record in records
    ] == [
        "doc-1:0",
        "doc-1:1",
        "doc-1:2",
    ]


def test_generate_batch_requires_sequence():
    provider = LocalEmbeddingProvider(
        dimension=8
    )

    generator = EmbeddingGenerator(provider)

    with pytest.raises(TypeError):
        generator.generate_batch(
            "invalid"
        )


def test_generate_batch_empty_sequence():
    provider = LocalEmbeddingProvider(
        dimension=8
    )

    generator = EmbeddingGenerator(provider)

    assert generator.generate_batch([]) == []


def test_generated_embedding_is_deterministic():
    provider = LocalEmbeddingProvider(
        dimension=16
    )

    generator = EmbeddingGenerator(provider)

    chunk = create_chunk()

    first = generator.generate(chunk)
    second = generator.generate(chunk)

    assert first.vector == second.vector

def test_generate_rejects_non_vector_result():
    class InvalidProvider:
        def generate_embedding(self, text):
            return "invalid"

    generator = EmbeddingGenerator(
        InvalidProvider()
    )

    with pytest.raises(TypeError):
        generator.generate(
            create_chunk()
        )


def test_generate_rejects_empty_vector():
    class InvalidProvider:
        def generate_embedding(self, text):
            return []

    generator = EmbeddingGenerator(
        InvalidProvider()
    )

    with pytest.raises(ValueError):
        generator.generate(
            create_chunk()
        )


def test_generate_rejects_non_numeric_vector_values():
    class InvalidProvider:
        def generate_embedding(self, text):
            return [0.1, "invalid", 0.3]

    generator = EmbeddingGenerator(
        InvalidProvider()
    )

    with pytest.raises(TypeError):
        generator.generate(
            create_chunk()
        )


def test_generate_accepts_integer_vector_values():
    class IntegerProvider:
        def generate_embedding(self, text):
            return [1, 2, 3]

    generator = EmbeddingGenerator(
        IntegerProvider()
    )

    record = generator.generate(
        create_chunk()
    )

    assert record.vector == [1, 2, 3]


def test_batch_stops_when_invalid_embedding_is_returned():
    class InvalidProvider:
        def generate_embedding(self, text):
            if text == "Bad":
                return []

            return [0.1, 0.2]

    generator = EmbeddingGenerator(
        InvalidProvider()
    )

    chunks = [
        create_chunk(
            chunk_id="doc:0",
            text="Good",
        ),
        create_chunk(
            chunk_id="doc:1",
            text="Bad",
        ),
    ]

    with pytest.raises(ValueError):
        generator.generate_batch(
            chunks
        )