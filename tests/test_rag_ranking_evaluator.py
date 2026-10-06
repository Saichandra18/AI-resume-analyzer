"""Tests for ranking-aware RAG evaluation."""

import pytest

from app.rag.evaluation.ranking import RankingEvaluator
from app.rag.models import RetrievedChunk


def chunk(chunk_id, score=0.9):
    return RetrievedChunk(
        chunk_id=chunk_id,
        text=f"text for {chunk_id}",
        score=score,
    )


def test_relevant_chunk_at_rank_one():
    evaluator = RankingEvaluator()

    result = evaluator.evaluate(
        [
            chunk("relevant"),
            chunk("other"),
        ],
        ["relevant"],
    )

    assert result["hit"] == 1.0
    assert result["best_relevant_rank"] == 1
    assert result["reciprocal_rank"] == pytest.approx(1.0)
    assert result["relevant_ranks"] == [1]


def test_relevant_chunk_at_rank_two():
    evaluator = RankingEvaluator()

    result = evaluator.evaluate(
        [
            chunk("other"),
            chunk("relevant"),
        ],
        ["relevant"],
    )

    assert result["hit"] == 1.0
    assert result["best_relevant_rank"] == 2
    assert result["reciprocal_rank"] == pytest.approx(0.5)
    assert result["relevant_ranks"] == [2]


def test_no_relevant_chunk():
    evaluator = RankingEvaluator()

    result = evaluator.evaluate(
        [
            chunk("other-1"),
            chunk("other-2"),
        ],
        ["relevant"],
    )

    assert result["hit"] == 0.0
    assert result["best_relevant_rank"] is None
    assert result["reciprocal_rank"] == pytest.approx(0.0)
    assert result["relevant_ranks"] == []


def test_multiple_relevant_chunks():
    evaluator = RankingEvaluator()

    result = evaluator.evaluate(
        [
            chunk("other"),
            chunk("relevant-1"),
            chunk("relevant-2"),
        ],
        [
            "relevant-1",
            "relevant-2",
        ],
    )

    assert result["hit"] == 1.0
    assert result["best_relevant_rank"] == 2
    assert result["reciprocal_rank"] == pytest.approx(0.5)
    assert result["relevant_ranks"] == [2, 3]


def test_best_rank_uses_first_relevant_result():
    evaluator = RankingEvaluator()

    result = evaluator.evaluate(
        [
            chunk("relevant-1"),
            chunk("other"),
            chunk("relevant-2"),
        ],
        [
            "relevant-1",
            "relevant-2",
        ],
    )

    assert result["best_relevant_rank"] == 1
    assert result["reciprocal_rank"] == pytest.approx(1.0)


def test_top_k_changes_ranking_evaluation():
    evaluator = RankingEvaluator()

    results = evaluator.evaluate(
        [
            chunk("other-1"),
            chunk("other-2"),
            chunk("relevant"),
        ],
        ["relevant"],
        k=2,
    )

    assert results["hit"] == 0.0
    assert results["best_relevant_rank"] is None
    assert results["reciprocal_rank"] == 0.0


def test_top_k_includes_relevant_result():
    evaluator = RankingEvaluator()

    results = evaluator.evaluate(
        [
            chunk("other"),
            chunk("relevant"),
            chunk("other-2"),
        ],
        ["relevant"],
        k=2,
    )

    assert results["hit"] == 1.0
    assert results["best_relevant_rank"] == 2
    assert results["reciprocal_rank"] == pytest.approx(0.5)


def test_precision_and_recall_are_reported():
    evaluator = RankingEvaluator()

    results = evaluator.evaluate(
        [
            chunk("relevant"),
            chunk("other"),
        ],
        [
            "relevant",
            "missing",
        ],
    )

    assert results["precision"] == pytest.approx(0.5)
    assert results["recall"] == pytest.approx(0.5)


def test_empty_results():
    evaluator = RankingEvaluator()

    results = evaluator.evaluate(
        [],
        ["relevant"],
    )

    assert results["retrieved_count"] == 0
    assert results["hit"] == 0.0
    assert results["reciprocal_rank"] == 0.0
    assert results["best_relevant_rank"] is None


def test_empty_relevant_set():
    evaluator = RankingEvaluator()

    results = evaluator.evaluate(
        [
            chunk("chunk-1"),
        ],
        [],
    )

    assert results["relevant_count"] == 0
    assert results["hit"] == 0.0
    assert results["reciprocal_rank"] == 0.0
    assert results["precision"] == 0.0
    assert results["recall"] == 0.0


def test_multiple_evaluations():
    evaluator = RankingEvaluator()

    results = evaluator.evaluate_multiple(
        [
            {
                "retrieved_chunks": [
                    chunk("a"),
                    chunk("b"),
                ],
                "relevant_chunk_ids": ["a"],
            },
            {
                "retrieved_chunks": [
                    chunk("x"),
                    chunk("y"),
                ],
                "relevant_chunk_ids": ["y"],
            },
        ]
    )

    assert len(results) == 2
    assert results[0]["reciprocal_rank"] == pytest.approx(1.0)
    assert results[1]["reciprocal_rank"] == pytest.approx(0.5)


def test_aggregate_metrics():
    evaluator = RankingEvaluator()

    results = [
        evaluator.evaluate(
            [
                chunk("a"),
            ],
            ["a"],
        ),
        evaluator.evaluate(
            [
                chunk("x"),
                chunk("b"),
            ],
            ["b"],
        ),
    ]

    aggregate = evaluator.aggregate(results)

    assert aggregate["evaluation_count"] == 2
    assert aggregate["mean_reciprocal_rank"] == pytest.approx(0.75)
    assert aggregate["hit_rate"] == pytest.approx(1.0)
    assert aggregate["mean_precision"] == pytest.approx(0.75)
    assert aggregate["mean_recall"] == pytest.approx(1.0)


def test_empty_aggregate():
    evaluator = RankingEvaluator()

    result = evaluator.aggregate([])

    assert result == {
        "evaluation_count": 0,
        "mean_reciprocal_rank": 0.0,
        "hit_rate": 0.0,
        "mean_precision": 0.0,
        "mean_recall": 0.0,
    }


def test_invalid_evaluations_collection():
    evaluator = RankingEvaluator()

    with pytest.raises(TypeError):
        evaluator.evaluate_multiple(None)


def test_invalid_evaluation_item():
    evaluator = RankingEvaluator()

    with pytest.raises(TypeError):
        evaluator.evaluate_multiple(
            ["invalid"]
        )


def test_missing_retrieved_chunks():
    evaluator = RankingEvaluator()

    with pytest.raises(ValueError):
        evaluator.evaluate_multiple(
            [
                {
                    "relevant_chunk_ids": ["a"],
                }
            ]
        )


def test_missing_relevant_ids():
    evaluator = RankingEvaluator()

    with pytest.raises(ValueError):
        evaluator.evaluate_multiple(
            [
                {
                    "retrieved_chunks": [
                        chunk("a"),
                    ],
                }
            ]
        )


def test_invalid_aggregate_results():
    evaluator = RankingEvaluator()

    with pytest.raises(TypeError):
        evaluator.aggregate(None)


def test_invalid_k():
    evaluator = RankingEvaluator()

    with pytest.raises(ValueError):
        evaluator.evaluate(
            [
                chunk("a"),
            ],
            ["a"],
            k=0,
        )