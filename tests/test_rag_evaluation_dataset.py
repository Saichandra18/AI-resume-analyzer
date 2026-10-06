"""Tests for the RAG evaluation dataset and baselines."""

import pytest

from app.rag.evaluation.baseline import (
    RAGBaselineEvaluator,
)
from app.rag.evaluation.dataset import (
    RAGEvaluationDataset,
)
from app.rag.models import RetrievedChunk


def chunk(chunk_id, score=0.9):
    return RetrievedChunk(
        chunk_id=chunk_id,
        text=f"text for {chunk_id}",
        score=score,
    )


def test_dataset_contains_expected_cases():
    cases = RAGEvaluationDataset.all()

    assert len(cases) == 5

    assert {
        case["case_id"]
        for case in cases
    } == {
        "python_backend",
        "flask_api",
        "machine_learning",
        "cloud_platform",
        "irrelevant_query",
    }


def test_dataset_count():
    assert RAGEvaluationDataset.count() == 5


def test_get_case():
    case = RAGEvaluationDataset.get(
        "python_backend"
    )

    assert case["case_id"] == "python_backend"
    assert case["query"] == (
        "Python backend development"
    )
    assert "python-backend" in (
        case["relevant_chunk_ids"]
    )


def test_get_unknown_case():
    with pytest.raises(KeyError):
        RAGEvaluationDataset.get(
            "does-not-exist"
        )


def test_invalid_case_id():
    with pytest.raises(TypeError):
        RAGEvaluationDataset.get(None)


def test_all_returns_independent_case_objects():
    first = RAGEvaluationDataset.all()
    second = RAGEvaluationDataset.all()

    first[0]["case_id"] = "modified"

    assert second[0]["case_id"] == (
        "python_backend"
    )


def test_perfect_case_passes_baseline():
    evaluator = RAGBaselineEvaluator()

    case = RAGEvaluationDataset.get(
        "python_backend"
    )

    result = evaluator.evaluate_case(
        case,
        [
            chunk("python-backend"),
            chunk("flask-api"),
        ],
    )

    assert result["passed"] is True
    assert result["metrics"]["recall"] == pytest.approx(1.0)


def test_missing_relevant_result_fails_baseline():
    evaluator = RAGBaselineEvaluator()

    case = RAGEvaluationDataset.get(
        "flask_api"
    )

    result = evaluator.evaluate_case(
        case,
        [
            chunk("python-backend"),
            chunk("machine-learning"),
        ],
    )

    assert result["passed"] is False


def test_irrelevant_case_has_zero_relevance_thresholds():
    case = RAGEvaluationDataset.get(
        "irrelevant_query"
    )

    assert case["minimum_recall"] == 0.0
    assert case["minimum_precision"] == 0.0
    assert case["minimum_mrr"] == 0.0


def test_dataset_evaluation_passes_all_cases():
    evaluator = RAGBaselineEvaluator()

    cases = RAGEvaluationDataset.all()

    retrieval_results = {
        "python_backend": [
            chunk("python-backend"),
            chunk("flask-api"),
        ],
        "flask_api": [
            chunk("flask-api"),
        ],
        "machine_learning": [
            chunk("machine-learning"),
        ],
        "cloud_platform": [
            chunk("cloud-deployment"),
        ],
        "irrelevant_query": [],
    }

    result = evaluator.evaluate_dataset(
        cases,
        retrieval_results,
    )

    assert result["evaluation_count"] == 5
    assert result["passed_count"] == 5
    assert result["failed_count"] == 0
    assert result["pass_rate"] == pytest.approx(1.0)


def test_dataset_evaluation_counts_failures():
    evaluator = RAGBaselineEvaluator()

    cases = RAGEvaluationDataset.all()

    retrieval_results = {
        "python_backend": [],
        "flask_api": [
            chunk("flask-api"),
        ],
        "machine_learning": [
            chunk("machine-learning"),
        ],
        "cloud_platform": [
            chunk("cloud-deployment"),
        ],
        "irrelevant_query": [],
    }

    result = evaluator.evaluate_dataset(
        cases,
        retrieval_results,
    )

    assert result["evaluation_count"] == 5
    assert result["passed_count"] == 4
    assert result["failed_count"] == 1
    assert result["pass_rate"] == pytest.approx(0.8)


def test_missing_retrieval_result_is_rejected():
    evaluator = RAGBaselineEvaluator()

    case = RAGEvaluationDataset.get(
        "python_backend"
    )

    with pytest.raises(ValueError):
        evaluator.evaluate_dataset(
            [case],
            {},
        )


def test_invalid_cases_collection():
    evaluator = RAGBaselineEvaluator()

    with pytest.raises(TypeError):
        evaluator.evaluate_dataset(
            None,
            {},
        )


def test_invalid_retrieval_results():
    evaluator = RAGBaselineEvaluator()

    with pytest.raises(TypeError):
        evaluator.evaluate_dataset(
            [],
            None,
        )


def test_invalid_case_object():
    evaluator = RAGBaselineEvaluator()

    with pytest.raises(TypeError):
        evaluator.evaluate_case(
            "invalid",
            [],
        )


def test_missing_case_field():
    evaluator = RAGBaselineEvaluator()

    with pytest.raises(ValueError):
        evaluator.evaluate_case(
            {
                "case_id": "test",
            },
            [],
        )