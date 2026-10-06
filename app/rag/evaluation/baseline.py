"""Evaluate RAG retrieval results against dataset baselines."""

from app.rag.evaluation.ranking import RankingEvaluator


class RAGBaselineEvaluator:
    """Evaluate retrieval quality against predefined thresholds."""

    def __init__(
        self,
        ranking_evaluator=None,
    ):
        self.ranking_evaluator = (
            ranking_evaluator
            or RankingEvaluator()
        )

    def evaluate_case(
        self,
        case,
        retrieved_chunks,
    ):
        """Evaluate one dataset case."""

        if not isinstance(case, dict):
            raise TypeError(
                "case must be a dictionary."
            )

        required_fields = (
            "case_id",
            "relevant_chunk_ids",
            "k",
            "minimum_recall",
            "minimum_precision",
            "minimum_mrr",
        )

        for field in required_fields:
            if field not in case:
                raise ValueError(
                    f"case is missing {field}."
                )

        metrics = self.ranking_evaluator.evaluate(
            retrieved_chunks=retrieved_chunks,
            relevant_chunk_ids=case[
                "relevant_chunk_ids"
            ],
            k=case["k"],
        )

        passed = (
            metrics["recall"]
            >= case["minimum_recall"]
            and metrics["precision"]
            >= case["minimum_precision"]
            and metrics["reciprocal_rank"]
            >= case["minimum_mrr"]
        )

        return {
            "case_id": case["case_id"],
            "passed": passed,
            "metrics": metrics,
            "thresholds": {
                "minimum_recall": case[
                    "minimum_recall"
                ],
                "minimum_precision": case[
                    "minimum_precision"
                ],
                "minimum_mrr": case[
                    "minimum_mrr"
                ],
            },
        }

    def evaluate_dataset(
        self,
        cases,
        retrieval_results,
    ):
        """Evaluate multiple dataset cases.

        ``retrieval_results`` must be a dictionary mapping
        case IDs to retrieved chunk collections.
        """

        if not isinstance(
            cases,
            (list, tuple),
        ):
            raise TypeError(
                "cases must be a list or tuple."
            )

        if not isinstance(
            retrieval_results,
            dict,
        ):
            raise TypeError(
                "retrieval_results must be a dictionary."
            )

        results = []

        for case in cases:
            case_id = case.get("case_id")

            if case_id not in retrieval_results:
                raise ValueError(
                    f"Missing retrieval results for {case_id}."
                )

            results.append(
                self.evaluate_case(
                    case,
                    retrieval_results[case_id],
                )
            )

        passed_count = sum(
            1
            for result in results
            if result["passed"]
        )

        total_count = len(results)

        return {
            "evaluation_count": total_count,
            "passed_count": passed_count,
            "failed_count": (
                total_count - passed_count
            ),
            "pass_rate": (
                passed_count / total_count
                if total_count
                else 0.0
            ),
            "results": results,
        }