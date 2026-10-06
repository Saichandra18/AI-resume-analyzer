"""Validation utilities for grounded RAG evidence."""

from app.rag.models import GroundedEvidence, RetrievedChunk


class GroundingValidator:
    """Validate that RAG evidence remains traceable to retrieved chunks."""

    def validate(
        self,
        evidence,
        retrieved_chunks,
    ):
        """Validate grounded evidence against retrieved chunks."""

        if not isinstance(
            evidence,
            (list, tuple),
        ):
            raise TypeError(
                "evidence must be a list or tuple."
            )

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

        retrieved_ids = {
            chunk.chunk_id
            for chunk in retrieved_chunks
        }

        for item in evidence:
            self._validate_evidence_item(
                item,
                retrieved_ids,
            )

        return True

    @staticmethod
    def _validate_evidence_item(
        evidence,
        retrieved_ids,
    ):
        """Validate one grounded evidence item."""

        if not isinstance(
            evidence,
            GroundedEvidence,
        ):
            raise TypeError(
                "evidence must contain "
                "GroundedEvidence objects."
            )

        if not evidence.text.strip():
            raise ValueError(
                "Evidence text cannot be empty."
            )

        if not evidence.source_chunk_ids:
            raise ValueError(
                "Evidence must reference at least "
                "one source chunk."
            )

        missing_ids = [
            chunk_id
            for chunk_id in evidence.source_chunk_ids
            if chunk_id not in retrieved_ids
        ]

        if missing_ids:
            raise ValueError(
                "Evidence references chunks that were "
                "not retrieved."
            )

        if not evidence.claim.strip():
            raise ValueError(
                "Evidence claim cannot be empty."
            )

        if not isinstance(
            evidence.confidence,
            (int, float),
        ):
            raise TypeError(
                "Evidence confidence must be numeric."
            )

        if not 0.0 <= evidence.confidence <= 1.0:
            raise ValueError(
                "Evidence confidence must be between "
                "0.0 and 1.0."
            )

        if evidence.claim.strip() not in evidence.text:
            raise ValueError(
                "Evidence claim must be traceable "
                "to the evidence text."
            )