"""Tests for the deterministic local embedding provider."""

import pytest

from app.rag.embeddings.local import LocalEmbeddingProvider


def test_default_dimension():
    provider = LocalEmbeddingProvider()

    embedding = provider.generate_embedding(
        "Python"
    )

    assert len(embedding) == 384


def test_custom_dimension():
    provider = LocalEmbeddingProvider(
        dimension=128
    )

    embedding = provider.generate_embedding(
        "Python"
    )

    assert len(embedding) == 128


def test_embedding_is_deterministic():
    provider = LocalEmbeddingProvider(
        dimension=32
    )

    first = provider.generate_embedding(
        "Python Flask"
    )

    second = provider.generate_embedding(
        "Python Flask"
    )

    assert first == second


def test_different_text_produces_different_embedding():
    provider = LocalEmbeddingProvider(
        dimension=32
    )

    first = provider.generate_embedding(
        "Python"
    )

    second = provider.generate_embedding(
        "Java"
    )

    assert first != second


def test_embedding_is_normalized():
    provider = LocalEmbeddingProvider(
        dimension=32
    )

    embedding = provider.generate_embedding(
        "Python"
    )

    magnitude = sum(
        value * value
        for value in embedding
    ) ** 0.5

    assert magnitude == pytest.approx(
        1.0,
        abs=1e-6,
    )


def test_batch_embeddings():
    provider = LocalEmbeddingProvider(
        dimension=16
    )

    embeddings = provider.generate_embeddings(
        ["Python", "Flask", "RAG"]
    )

    assert len(embeddings) == 3
    assert all(
        len(embedding) == 16
        for embedding in embeddings
    )


def test_empty_text_raises_error():
    provider = LocalEmbeddingProvider()

    with pytest.raises(ValueError):
        provider.generate_embedding("")


def test_whitespace_text_raises_error():
    provider = LocalEmbeddingProvider()

    with pytest.raises(ValueError):
        provider.generate_embedding("   ")


def test_non_string_text_raises_error():
    provider = LocalEmbeddingProvider()

    with pytest.raises(TypeError):
        provider.generate_embedding(123)


def test_batch_requires_list_or_tuple():
    provider = LocalEmbeddingProvider()

    with pytest.raises(TypeError):
        provider.generate_embeddings("Python")


def test_invalid_dimension_type():
    with pytest.raises(TypeError):
        LocalEmbeddingProvider(
            dimension="384"
        )


def test_invalid_dimension_value():
    with pytest.raises(ValueError):
        LocalEmbeddingProvider(
            dimension=0
        )