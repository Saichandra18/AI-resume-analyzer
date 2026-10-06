"""Tests for RAG provider interfaces."""

import pytest

from app.rag.interfaces import (
    EmbeddingProvider,
    VectorStore,
)


def test_embedding_provider_cannot_be_instantiated():
    with pytest.raises(TypeError):
        EmbeddingProvider()


def test_vector_store_cannot_be_instantiated():
    with pytest.raises(TypeError):
        VectorStore()


def test_embedding_provider_requires_single_embedding_method():
    methods = {
        "generate_embedding",
        "generate_embeddings",
    }

    assert methods.issubset(
        set(EmbeddingProvider.__abstractmethods__)
    )


def test_vector_store_requires_expected_methods():
    methods = {
        "add",
        "search",
        "delete",
        "count",
    }

    assert methods.issubset(
        set(VectorStore.__abstractmethods__)
    )


class DummyEmbeddingProvider(EmbeddingProvider):
    """Concrete implementation used only for interface testing."""

    def generate_embedding(self, text):
        return [0.1, 0.2]

    def generate_embeddings(self, texts):
        return [
            self.generate_embedding(text)
            for text in texts
        ]


class DummyVectorStore(VectorStore):
    """Concrete implementation used only for interface testing."""

    def __init__(self):
        self.records = {}

    def add(self, records):
        for record in records:
            self.records[record.chunk_id] = record

    def search(
        self,
        query_vector,
        top_k=5,
        filters=None,
    ):
        return []

    def delete(self, chunk_ids):
        for chunk_id in chunk_ids:
            self.records.pop(chunk_id, None)

    def count(self):
        return len(self.records)


def test_embedding_provider_can_be_implemented():
    provider = DummyEmbeddingProvider()

    assert provider.generate_embedding(
        "Python"
    ) == [0.1, 0.2]

    assert provider.generate_embeddings(
        ["Python", "Flask"]
    ) == [
        [0.1, 0.2],
        [0.1, 0.2],
    ]


def test_vector_store_can_be_implemented():
    store = DummyVectorStore()

    assert store.count() == 0

    store.delete(["missing"])

    assert store.count() == 0