"""Ranking-aware metrics for RAG retrieval evaluation."""

from app.rag.models import RetrievedChunk


class RankingEvaluator:
    """Evaluate the ranking position of relevant chunks."""

    def evaluate(
        self,
        retrieved_chunks,
        relevant_chunk_ids,
        k=None,
    ):
        """Return ranking-aware retrieval metrics."""

        self._validate_retrieved_chunks(
            retrieved_chunks
        )

        self._validate_relevant_ids(
            relevant_chunk_ids
        )

        if k is not None:
            if not isinstance(k, int) or k < 1:
                raise ValueError(
                    "k must be a positive integer."
                )

            evaluated_chunks = list(
                retrieved_chunks[:k]
            )
        else:
            evaluated_chunks = list(
                retrieved_chunks
            )

        relevant_ids = {
            str(chunk_id)
            for chunk_id in relevant_chunk_ids
        }

        ranks = []

        for index, chunk in enumerate(
            evaluated_chunks,
            start=1,
        ):
            if chunk.chunk_id in relevant_ids:
                ranks.append(index)

        hit = 1.0 if ranks else 0.0

        reciprocal_rank = (
            1.0 / min(ranks)
            if ranks
            else 0.0
        )

        relevant_count = len(
            relevant_ids
        )

        retrieved_count = len(
            evaluated_chunks
        )

        relevant_retrieved_count = len(
            set(
                chunk.chunk_id
                for chunk in evaluated_chunks
            )
            & relevant_ids
        )

        precision = (
            relevant_retrieved_count
            / retrieved_count
            if retrieved_count
            else 0.0
        )

        recall = (
            relevant_retrieved_count
            / relevant_count
            if relevant_count
            else 0.0
        )

        return {
            "k": (
                k
                if k is not None
                else retrieved_count
            ),
            "retrieved_count": retrieved_count,
            "relevant_count": relevant_count,
            "relevant_retrieved_count": (
                relevant_retrieved_count
            ),
            "hit": hit,
            "reciprocal_rank": reciprocal_rank,
            "best_relevant_rank": (
                min(ranks)
                if ranks
                else None
            ),
            "relevant_ranks": ranks,
            "precision": precision,
            "recall": recall,
        }

    def evaluate_multiple(
        self,
        evaluations,
    ):
        """Evaluate multiple retrieval result sets.

        Each item must be a dictionary containing:

            retrieved_chunks
            relevant_chunk_ids

        An optional ``k`` may also be supplied.
        """

        if not isinstance(
            evaluations,
            (list, tuple),
        ):
            raise TypeError(
                "evaluations must be a list or tuple."
            )

        results = []

        for item in evaluations:
            if not isinstance(item, dict):
                raise TypeError(
                    "Each evaluation must be a dictionary."
                )

            if (
                "retrieved_chunks"
                not in item
            ):
                raise ValueError(
                    "Evaluation is missing "
                    "retrieved_chunks."
                )

            if (
                "relevant_chunk_ids"
                not in item
            ):
                raise ValueError(
                    "Evaluation is missing "
                    "relevant_chunk_ids."
                )

            results.append(
                self.evaluate(
                    retrieved_chunks=item[
                        "retrieved_chunks"
                    ],
                    relevant_chunk_ids=item[
                        "relevant_chunk_ids"
                    ],
                    k=item.get("k"),
                )
            )

        return results

    def aggregate(
        self,
        results,
    ):
        """Aggregate ranking metrics across evaluations."""

        if not isinstance(
            results,
            (list, tuple),
        ):
            raise TypeError(
                "results must be a list or tuple."
            )

        if not results:
            return {
                "evaluation_count": 0,
                "mean_reciprocal_rank": 0.0,
                "hit_rate": 0.0,
                "mean_precision": 0.0,
                "mean_recall": 0.0,
            }

        for result in results:
            if not isinstance(result, dict):
                raise TypeError(
                    "Each result must be a dictionary."
                )

        count = len(results)

        return {
            "evaluation_count": count,
            "mean_reciprocal_rank": (
                sum(
                    result["reciprocal_rank"]
                    for result in results
                )
                / count
            ),
            "hit_rate": (
                sum(
                    result["hit"]
                    for result in results
                )
                / count
            ),
            "mean_precision": (
                sum(
                    result["precision"]
                    for result in results
                )
                / count
            ),
            "mean_recall": (
                sum(
                    result["recall"]
                    for result in results
                )
                / count
            ),
        }

    @staticmethod
    def _validate_retrieved_chunks(
        retrieved_chunks,
    ):
        if not isinstance(
            retrieved_chunks,
            (list, tuple),
        ):
            raise TypeError(
                "retrieved_chunks must be a list or tuple."
            )

        for chunk in retrieved_chunks:
            if not isinstance(
                chunk,
                RetrievedChunk,
            ):
                raise TypeError(
                    "retrieved_chunks must contain "
                    "RetrievedChunk objects."
                )

    @staticmethod
    def _validate_relevant_ids(
        relevant_chunk_ids,
    ):
        if not isinstance(
            relevant_chunk_ids,
            (list, tuple, set),
        ):
            raise TypeError(
                "relevant_chunk_ids must be a list, "
                "tuple, or set."
            )