"""Tests for RAG retrieval evaluation metrics."""

import pytest

from app.rag.models import RetrievedChunk
from app.rag.evaluation.retrieval import RetrievalEvaluator


def make_chunk(
    chunk_id,
    score,
):
    return RetrievedChunk(
        chunk_id=chunk_id,
        text=f"text for {chunk_id}",
        score=score,
    )


def test_perfect_retrieval():
    evaluator = RetrievalEvaluator()

    results = evaluator.evaluate(
        retrieved_chunks=[
            make_chunk("chunk-1", 0.95),
            make_chunk("chunk-2", 0.90),
        ],
        relevant_chunk_ids=[
            "chunk-1",
            "chunk-2",
        ],
    )

    assert results["retrieved_count"] == 2
    assert results["relevant_count"] == 2
    assert results["true_positive_count"] == 2
    assert results["precision"] == pytest.approx(1.0)
    assert results["recall"] == pytest.approx(1.0)
    assert results["f1"] == pytest.approx(1.0)


def test_no_relevant_results():
    evaluator = RetrievalEvaluator()

    results = evaluator.evaluate(
        retrieved_chunks=[
            make_chunk("chunk-1", 0.95),
            make_chunk("chunk-2", 0.90),
        ],
        relevant_chunk_ids=[
            "chunk-3",
            "chunk-4",
        ],
    )

    assert results["true_positive_count"] == 0
    assert results["precision"] == pytest.approx(0.0)
    assert results["recall"] == pytest.approx(0.0)
    assert results["f1"] == pytest.approx(0.0)


def test_partial_retrieval():
    evaluator = RetrievalEvaluator()

    results = evaluator.evaluate(
        retrieved_chunks=[
            make_chunk("chunk-1", 0.95),
            make_chunk("chunk-3", 0.80),
        ],
        relevant_chunk_ids=[
            "chunk-1",
            "chunk-2",
        ],
    )

    assert results["true_positive_count"] == 1
    assert results["precision"] == pytest.approx(0.5)
    assert results["recall"] == pytest.approx(0.5)
    assert results["f1"] == pytest.approx(0.5)


def test_top_k_evaluation():
    evaluator = RetrievalEvaluator()

    results = evaluator.evaluate(
        retrieved_chunks=[
            make_chunk("chunk-1", 0.95),
            make_chunk("chunk-2", 0.90),
            make_chunk("chunk-3", 0.80),
        ],
        relevant_chunk_ids=[
            "chunk-1",
            "chunk-3",
        ],
        k=2,
    )

    assert results["k"] == 2
    assert results["retrieved_count"] == 2
    assert results["true_positive_count"] == 1
    assert results["precision"] == pytest.approx(0.5)
    assert results["recall"] == pytest.approx(0.5)


def test_average_score():
    evaluator = RetrievalEvaluator()

    results = evaluator.evaluate(
        retrieved_chunks=[
            make_chunk("chunk-1", 0.90),
            make_chunk("chunk-2", 0.70),
        ],
        relevant_chunk_ids=[
            "chunk-1",
        ],
    )

    assert results["average_score"] == pytest.approx(0.80)


def test_empty_retrieval():
    evaluator = RetrievalEvaluator()

    results = evaluator.evaluate(
        retrieved_chunks=[],
        relevant_chunk_ids=[
            "chunk-1",
        ],
    )

    assert results["retrieved_count"] == 0
    assert results["true_positive_count"] == 0
    assert results["precision"] == pytest.approx(0.0)
    assert results["recall"] == pytest.approx(0.0)
    assert results["f1"] == pytest.approx(0.0)
    assert results["average_score"] == pytest.approx(0.0)


def test_empty_relevant_set():
    evaluator = RetrievalEvaluator()

    results = evaluator.evaluate(
        retrieved_chunks=[
            make_chunk("chunk-1", 0.90),
        ],
        relevant_chunk_ids=[],
    )

    assert results["relevant_count"] == 0
    assert results["true_positive_count"] == 0
    assert results["precision"] == pytest.approx(0.0)
    assert results["recall"] == pytest.approx(0.0)
    assert results["f1"] == pytest.approx(0.0)


def test_duplicate_retrieved_ids_do_not_inflate_true_positive_count():
    evaluator = RetrievalEvaluator()

    results = evaluator.evaluate(
        retrieved_chunks=[
            make_chunk("chunk-1", 0.95),
            make_chunk("chunk-1", 0.90),
        ],
        relevant_chunk_ids=[
            "chunk-1",
        ],
    )

    assert results["retrieved_count"] == 2
    assert results["true_positive_count"] == 1
    assert results["precision"] == pytest.approx(0.5)
    assert results["recall"] == pytest.approx(1.0)


def test_relevant_ids_can_be_a_set():
    evaluator = RetrievalEvaluator()

    results = evaluator.evaluate(
        retrieved_chunks=[
            make_chunk("chunk-1", 0.90),
        ],
        relevant_chunk_ids={
            "chunk-1",
        },
    )

    assert results["true_positive_count"] == 1
    assert results["precision"] == pytest.approx(1.0)
    assert results["recall"] == pytest.approx(1.0)


def test_invalid_retrieved_chunks_are_rejected():
    evaluator = RetrievalEvaluator()

    with pytest.raises(TypeError):
        evaluator.evaluate(
            retrieved_chunks=["chunk-1"],
            relevant_chunk_ids=["chunk-1"],
        )


def test_invalid_retrieved_collection_is_rejected():
    evaluator = RetrievalEvaluator()

    with pytest.raises(TypeError):
        evaluator.evaluate(
            retrieved_chunks=None,
            relevant_chunk_ids=["chunk-1"],
        )


def test_invalid_relevant_ids_are_rejected():
    evaluator = RetrievalEvaluator()

    with pytest.raises(TypeError):
        evaluator.evaluate(
            retrieved_chunks=[],
            relevant_chunk_ids=None,
        )


def test_invalid_k_is_rejected():
    evaluator = RetrievalEvaluator()

    with pytest.raises(ValueError):
        evaluator.evaluate(
            retrieved_chunks=[
                make_chunk("chunk-1", 0.90),
            ],
            relevant_chunk_ids=[
                "chunk-1",
            ],
            k=0,
        )


def test_metrics_are_deterministic():
    evaluator = RetrievalEvaluator()

    retrieved = [
        make_chunk("chunk-1", 0.95),
        make_chunk("chunk-2", 0.85),
    ]

    relevant = [
        "chunk-1",
    ]

    first = evaluator.evaluate(
        retrieved,
        relevant,
    )

    second = evaluator.evaluate(
        retrieved,
        relevant,
    )

    assert first == second