"""Build RAG context from retrieved chunks and grounded evidence."""

from app.rag.models import (
    GroundedEvidence,
    RAGContext,
    RetrievedChunk,
    RetrievalQuery,
)


class RAGContextBuilder:
    """Build a standardized RAGContext object."""

    def build(
        self,
        retrieved_chunks,
        grounded_evidence,
        query=None,
        metadata=None,
    ):
        """Build a RAGContext from retrieval and grounding results."""

        if not isinstance(
            retrieved_chunks,
            (list, tuple),
        ):
            raise TypeError(
                "retrieved_chunks must be a list or tuple."
            )

        if not isinstance(
            grounded_evidence,
            (list, tuple),
        ):
            raise TypeError(
                "grounded_evidence must be a list or tuple."
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

        for evidence in grounded_evidence:
            if not isinstance(
                evidence,
                GroundedEvidence,
            ):
                raise TypeError(
                    "grounded_evidence must contain "
                    "GroundedEvidence objects."
                )

        if query is not None and not isinstance(
            query,
            (RetrievalQuery, dict),
        ):
            raise TypeError(
                "query must be a RetrievalQuery or dictionary."
            )

        if metadata is not None and not isinstance(
            metadata,
            dict,
        ):
            raise TypeError(
                "metadata must be a dictionary."
            )

        return RAGContext(
            query=query,
            retrieved_chunks=list(
                retrieved_chunks
            ),
            evidence=list(
                grounded_evidence
            ),
            metadata=dict(
                metadata or {}
            ),
        )