"""Tests for RAG retrieval quality and ranking behavior."""

import pytest

from app.rag.embeddings.local import LocalEmbeddingProvider
from app.rag.models import (
    DocumentChunk,
    EmbeddingRecord,
    RetrievalQuery,
    RetrievedChunk,
)
from app.rag.retrieval.hydrator import RetrievalHydrator
from app.rag.retrieval.service import RetrievalService
from app.rag.vectorstore.in_memory import InMemoryVectorStore
from app.rag.vectorstore.registry import ChunkRegistry


def make_provider():
    return LocalEmbeddingProvider(dimension=16)


def make_store(provider, texts):
    store = InMemoryVectorStore()

    records = []

    for index, text in enumerate(texts):
        vector = provider.generate_embedding(text)

        records.append(
            EmbeddingRecord(
                chunk_id=f"chunk-{index}",
                vector=vector,
                model="test",
                dimensions=len(vector),
            )
        )

    store.add(records)

    return store


def test_top_k_limits_number_of_results():
    provider = make_provider()

    store = make_store(
        provider,
        [
            "Python backend development",
            "Python Flask REST API",
            "Machine learning models",
            "Frontend JavaScript development",
        ],
    )

    service = RetrievalService(
        embedding_provider=provider,
        vector_store=store,
    )

    query = RetrievalQuery(
        query="Python backend",
        top_k=2,
    )

    results = service.retrieve(query)

    assert len(results) <= 2


def test_results_are_sorted_by_descending_score():
    provider = make_provider()

    store = make_store(
        provider,
        [
            "Python backend development",
            "Python Flask REST API",
            "Machine learning models",
            "Frontend JavaScript development",
        ],
    )

    service = RetrievalService(
        embedding_provider=provider,
        vector_store=store,
    )

    query = RetrievalQuery(
        query="Python backend",
        top_k=4,
    )

    results = service.retrieve(query)

    scores = [result.score for result in results]

    assert scores == sorted(
        scores,
        reverse=True,
    )


def test_retrieval_is_deterministic():
    provider = make_provider()

    store = make_store(
        provider,
        [
            "Python backend development",
            "Python Flask REST API",
            "Machine learning models",
            "Frontend JavaScript development",
        ],
    )

    service = RetrievalService(
        embedding_provider=provider,
        vector_store=store,
    )

    query = RetrievalQuery(
        query="Python backend",
        top_k=4,
    )

    first = service.retrieve(query)
    second = service.retrieve(query)

    assert [
        result.chunk_id for result in first
    ] == [
        result.chunk_id for result in second
    ]

    assert [
        result.score for result in first
    ] == pytest.approx(
        [
            result.score for result in second
        ]
    )


def test_more_relevant_python_content_ranks_above_unrelated_content():
    provider = make_provider()

    store = make_store(
        provider,
        [
            "Python backend development with Flask and REST APIs",
            "Python programming and backend services",
            "Cooking recipes and food preparation",
            "Photography equipment and camera lenses",
        ],
    )

    service = RetrievalService(
        embedding_provider=provider,
        vector_store=store,
    )

    query = RetrievalQuery(
        query="Python backend Flask REST API",
        top_k=4,
    )

    results = service.retrieve(query)

    assert len(results) == 4

    top_ids = [
        result.chunk_id
        for result in results[:2]
    ]

    assert "chunk-0" in top_ids


def test_top_k_one_returns_single_best_result():
    provider = make_provider()

    store = make_store(
        provider,
        [
            "Python backend development",
            "Machine learning models",
            "Frontend JavaScript",
        ],
    )

    service = RetrievalService(
        embedding_provider=provider,
        vector_store=store,
    )

    query = RetrievalQuery(
        query="Python backend",
        top_k=1,
    )

    results = service.retrieve(query)

    assert len(results) == 1


def test_empty_store_returns_empty_results():
    provider = make_provider()
    store = InMemoryVectorStore()

    service = RetrievalService(
        embedding_provider=provider,
        vector_store=store,
    )

    query = RetrievalQuery(
        query="Python backend",
        top_k=5,
    )

    assert service.retrieve(query) == []


def test_metadata_filter_limits_retrieval_results():
    provider = make_provider()

    store = InMemoryVectorStore()

    store.add(
        [
            EmbeddingRecord(
                chunk_id="experience",
                vector=provider.generate_embedding(
                    "Python backend experience"
                ),
                model="test",
                dimensions=16,
                metadata={
                    "section": "experience",
                },
            ),
            EmbeddingRecord(
                chunk_id="projects",
                vector=provider.generate_embedding(
                    "Python backend project"
                ),
                model="test",
                dimensions=16,
                metadata={
                    "section": "projects",
                },
            ),
        ]
    )

    service = RetrievalService(
        embedding_provider=provider,
        vector_store=store,
    )

    query = RetrievalQuery(
        query="Python backend",
        top_k=5,
        filters={
            "section": "experience",
        },
    )

    results = service.retrieve(query)

    assert len(results) == 1
    assert results[0].chunk_id == "experience"


def test_hydration_preserves_ranking_and_scores():
    provider = make_provider()

    store = make_store(
        provider,
        [
            "Python backend development",
            "Machine learning models",
            "Frontend JavaScript development",
        ],
    )

    service = RetrievalService(
        embedding_provider=provider,
        vector_store=store,
    )

    query = RetrievalQuery(
        query="Python backend",
        top_k=3,
    )

    retrieved = service.retrieve(query)

    registry = ChunkRegistry()

    registry.add(
        [
            DocumentChunk(
                chunk_id="chunk-0",
                document_id="doc-1",
                text="Python backend development",
                chunk_index=0,
            ),
            DocumentChunk(
                chunk_id="chunk-1",
                document_id="doc-1",
                text="Machine learning models",
                chunk_index=1,
            ),
            DocumentChunk(
                chunk_id="chunk-2",
                document_id="doc-1",
                text="Frontend JavaScript development",
                chunk_index=2,
            ),
        ]
    )

    hydrator = RetrievalHydrator(registry)

    hydrated = hydrator.hydrate(retrieved)

    assert [
        item.chunk_id for item in hydrated
    ] == [
        item.chunk_id for item in retrieved
    ]

    assert [
        item.score for item in hydrated
    ] == pytest.approx(
        [
            item.score for item in retrieved
        ]
    )


def test_hydrated_results_contain_original_text():
    provider = make_provider()

    store = make_store(
        provider,
        [
            "Python backend development",
            "Machine learning models",
        ],
    )

    service = RetrievalService(
        embedding_provider=provider,
        vector_store=store,
    )

    query = RetrievalQuery(
        query="Python backend",
        top_k=2,
    )

    retrieved = service.retrieve(query)

    registry = ChunkRegistry()

    registry.add(
        [
            DocumentChunk(
                chunk_id="chunk-0",
                document_id="doc-1",
                text="Python backend development",
                chunk_index=0,
            ),
            DocumentChunk(
                chunk_id="chunk-1",
                document_id="doc-1",
                text="Machine learning models",
                chunk_index=1,
            ),
        ]
    )

    hydrated = RetrievalHydrator(
        registry
    ).hydrate(retrieved)

    assert all(
        isinstance(item.text, str)
        and item.text
        for item in hydrated
    )


def test_retrieval_scores_are_numeric():
    provider = make_provider()

    store = make_store(
        provider,
        [
            "Python backend development",
            "Machine learning models",
        ],
    )

    service = RetrievalService(
        embedding_provider=provider,
        vector_store=store,
    )

    query = RetrievalQuery(
        query="Python",
        top_k=2,
    )

    results = service.retrieve(query)

    assert all(
        isinstance(result.score, float)
        for result in results
    )


def test_retrieval_result_ids_are_unique():
    provider = make_provider()

    store = make_store(
        provider,
        [
            "Python backend development",
            "Python Flask REST API",
            "Machine learning models",
        ],
    )

    service = RetrievalService(
        embedding_provider=provider,
        vector_store=store,
    )

    query = RetrievalQuery(
        query="Python",
        top_k=10,
    )

    results = service.retrieve(query)

    ids = [
        result.chunk_id
        for result in results
    ]

    assert len(ids) == len(set(ids))


def test_query_filter_and_top_k_work_together():
    provider = make_provider()

    store = InMemoryVectorStore()

    store.add(
        [
            EmbeddingRecord(
                chunk_id="experience-1",
                vector=provider.generate_embedding(
                    "Python backend development"
                ),
                model="test",
                dimensions=16,
                metadata={
                    "section": "experience",
                },
            ),
            EmbeddingRecord(
                chunk_id="experience-2",
                vector=provider.generate_embedding(
                    "Python API development"
                ),
                model="test",
                dimensions=16,
                metadata={
                    "section": "experience",
                },
            ),
            EmbeddingRecord(
                chunk_id="project-1",
                vector=provider.generate_embedding(
                    "Python project"
                ),
                model="test",
                dimensions=16,
                metadata={
                    "section": "projects",
                },
            ),
        ]
    )

    service = RetrievalService(
        embedding_provider=provider,
        vector_store=store,
    )

    query = RetrievalQuery(
        query="Python backend",
        top_k=1,
        filters={
            "section": "experience",
        },
    )

    results = service.retrieve(query)

    assert len(results) == 1
    assert results[0].chunk_id.startswith(
        "experience"
    )