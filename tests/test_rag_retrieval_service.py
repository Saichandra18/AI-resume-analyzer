import pytest

from app.rag.models import RetrievalQuery
from app.rag.retrieval.service import RetrievalService


class DummyEmbeddingProvider:
    def __init__(self, vector=None):
        self.vector = vector or [1.0, 0.0]
        self.received_text = None

    def generate_embedding(self, text):
        self.received_text = text
        return self.vector


class DummyVectorStore:
    def __init__(self):
        self.received_vector = None
        self.received_top_k = None
        self.received_filters = None

    def search(self, query_vector, top_k=5, filters=None):
        self.received_vector = query_vector
        self.received_top_k = top_k
        self.received_filters = filters

        return ["retrieved"]


def test_retrieve_generates_query_embedding():
    provider = DummyEmbeddingProvider(
        vector=[0.5, 0.5],
    )
    store = DummyVectorStore()

    service = RetrievalService(
        provider,
        store,
    )

    query = RetrievalQuery(
        query="Python Flask developer",
        top_k=3,
    )

    results = service.retrieve(query)

    assert results == ["retrieved"]
    assert provider.received_text == (
        "Python Flask developer"
    )


def test_retrieve_passes_embedding_to_vector_store():
    provider = DummyEmbeddingProvider(
        vector=[0.2, 0.8],
    )
    store = DummyVectorStore()

    service = RetrievalService(
        provider,
        store,
    )

    query = RetrievalQuery(
        query="machine learning",
    )

    service.retrieve(query)

    assert store.received_vector == [0.2, 0.8]


def test_retrieve_passes_top_k():
    provider = DummyEmbeddingProvider()
    store = DummyVectorStore()

    service = RetrievalService(
        provider,
        store,
    )

    query = RetrievalQuery(
        query="Python",
        top_k=7,
    )

    service.retrieve(query)

    assert store.received_top_k == 7


def test_retrieve_passes_filters():
    provider = DummyEmbeddingProvider()
    store = DummyVectorStore()

    service = RetrievalService(
        provider,
        store,
    )

    query = RetrievalQuery(
        query="Python",
        top_k=5,
        filters={
            "section": "skills",
        },
    )

    service.retrieve(query)

    assert store.received_filters == {
        "section": "skills",
    }


def test_retrieve_rejects_invalid_query():
    provider = DummyEmbeddingProvider()
    store = DummyVectorStore()

    service = RetrievalService(
        provider,
        store,
    )

    with pytest.raises(TypeError):
        service.retrieve("Python")


def test_retrieval_service_requires_embedding_provider():
    store = DummyVectorStore()

    with pytest.raises(ValueError):
        RetrievalService(
            None,
            store,
        )


def test_retrieval_service_requires_vector_store():
    provider = DummyEmbeddingProvider()

    with pytest.raises(ValueError):
        RetrievalService(
            provider,
            None,
        )


def test_retrieval_service_validates_embedding_provider():
    store = DummyVectorStore()

    with pytest.raises(TypeError):
        RetrievalService(
            object(),
            store,
        )


def test_retrieval_service_validates_vector_store():
    provider = DummyEmbeddingProvider()

    with pytest.raises(TypeError):
        RetrievalService(
            provider,
            object(),
        )