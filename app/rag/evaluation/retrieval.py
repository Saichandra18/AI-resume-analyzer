"""Metrics for evaluating RAG retrieval quality."""

from app.rag.models import RetrievedChunk


class RetrievalEvaluator:
    """Evaluate retrieval results against expected chunk IDs."""

    def evaluate(
        self,
        retrieved_chunks,
        relevant_chunk_ids,
        k=None,
    ):
        """Return deterministic retrieval quality metrics."""

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

        retrieved_ids = [
            chunk.chunk_id
            for chunk in evaluated_chunks
        ]

        relevant_ids = set(
            str(chunk_id)
            for chunk_id in relevant_chunk_ids
        )

        retrieved_id_set = set(
            retrieved_ids
        )

        relevant_retrieved_ids = (
            retrieved_id_set & relevant_ids
        )

        retrieved_count = len(
            retrieved_ids
        )

        relevant_count = len(
            relevant_ids
        )

        true_positive_count = len(
            relevant_retrieved_ids
        )

        precision = (
            true_positive_count
            / retrieved_count
            if retrieved_count
            else 0.0
        )

        recall = (
            true_positive_count
            / relevant_count
            if relevant_count
            else 0.0
        )

        if precision + recall:
            f1 = (
                2 * precision * recall
                / (precision + recall)
            )
        else:
            f1 = 0.0

        average_score = (
            sum(
                chunk.score
                for chunk in evaluated_chunks
            )
            / retrieved_count
            if retrieved_count
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
            "true_positive_count": (
                true_positive_count
            ),
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "average_score": average_score,
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