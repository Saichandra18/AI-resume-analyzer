"""Build grounded evidence from retrieved RAG chunks."""

from app.rag.models import GroundedEvidence, RetrievedChunk


class EvidenceBuilder:
    """Convert retrieved chunks into traceable grounded evidence."""

    def build(self, retrieved_chunks):
        """Build grounded evidence from retrieved chunks."""

        if not isinstance(
            retrieved_chunks,
            (list, tuple),
        ):
            raise TypeError(
                "retrieved_chunks must be a list or tuple."
            )

        evidence = []

        for index, chunk in enumerate(
            retrieved_chunks
        ):
            if not isinstance(
                chunk,
                RetrievedChunk,
            ):
                raise TypeError(
                    "retrieved_chunks must contain "
                    "RetrievedChunk objects."
                )

            evidence.append(
                self._build_evidence(
                    chunk,
                    index,
                )
            )

        return evidence

    @staticmethod
    def _build_evidence(
        chunk,
        index,
    ):
        """Build one grounded evidence item."""

        metadata = dict(chunk.metadata)

        metadata.setdefault(
            "document_id",
            chunk.document_id,
        )

        metadata.setdefault(
            "retrieval_score",
            chunk.score,
        )

        return GroundedEvidence(
            evidence_id=f"evidence:{index}",
            text=chunk.text,
            source_chunk_ids=[
                chunk.chunk_id,
            ],
            claim=chunk.text,
            confidence=chunk.score,
            metadata=metadata,
        )