"""Evaluation metrics for RAG evidence and recommendation grounding."""

from app.rag.models import GroundedEvidence, RetrievedChunk
from app.rag.recommendations.safety import (
    RecommendationSafetyResult,
)


class GroundingEvaluator:
    """Evaluate evidence traceability and recommendation safety."""

    def evaluate_evidence(
        self,
        evidence,
        retrieved_chunks,
    ):
        """Evaluate evidence coverage against retrieved chunks."""

        self._validate_evidence(evidence)
        self._validate_retrieved_chunks(
            retrieved_chunks
        )

        retrieved_ids = {
            chunk.chunk_id
            for chunk in retrieved_chunks
        }

        total_evidence = len(evidence)
        grounded_evidence = 0
        invalid_evidence = 0

        evidence_coverage = []

        for item in evidence:
            source_ids = set(
                item.source_chunk_ids
            )

            matched_ids = (
                source_ids & retrieved_ids
            )

            is_grounded = bool(
                source_ids
                and matched_ids
                and item.text.strip()
                and item.claim.strip()
            )

            if is_grounded:
                grounded_evidence += 1
            else:
                invalid_evidence += 1

            evidence_coverage.append(
                {
                    "evidence_id": item.evidence_id,
                    "grounded": is_grounded,
                    "source_chunk_count": len(
                        source_ids
                    ),
                    "matched_chunk_count": len(
                        matched_ids
                    ),
                }
            )

        grounding_rate = (
            grounded_evidence / total_evidence
            if total_evidence
            else 0.0
        )

        return {
            "evidence_count": total_evidence,
            "grounded_evidence_count": (
                grounded_evidence
            ),
            "invalid_evidence_count": (
                invalid_evidence
            ),
            "grounding_rate": grounding_rate,
            "evidence_coverage": evidence_coverage,
        }

    def evaluate_safety(
        self,
        safety_results,
    ):
        """Evaluate recommendation safety results."""

        if not isinstance(
            safety_results,
            (list, tuple),
        ):
            raise TypeError(
                "safety_results must be a list or tuple."
            )

        for result in safety_results:
            if not isinstance(
                result,
                RecommendationSafetyResult,
            ):
                raise TypeError(
                    "safety_results must contain "
                    "RecommendationSafetyResult objects."
                )

        total = len(safety_results)

        safe_count = sum(
            1
            for result in safety_results
            if result.safe
        )

        unsafe_count = total - safe_count

        safety_rate = (
            safe_count / total
            if total
            else 0.0
        )

        return {
            "recommendation_count": total,
            "safe_count": safe_count,
            "unsafe_count": unsafe_count,
            "safety_rate": safety_rate,
        }

    def evaluate(
        self,
        evidence,
        retrieved_chunks,
        safety_results=None,
    ):
        """Evaluate the complete grounding pipeline."""

        evidence_metrics = self.evaluate_evidence(
            evidence,
            retrieved_chunks,
        )

        safety_metrics = self.evaluate_safety(
            safety_results or []
        )

        return {
            "evidence": evidence_metrics,
            "safety": safety_metrics,
            "overall_grounding_rate": (
                evidence_metrics[
                    "grounding_rate"
                ]
            ),
            "overall_safety_rate": (
                safety_metrics[
                    "safety_rate"
                ]
            ),
        }

    @staticmethod
    def _validate_evidence(evidence):
        if not isinstance(
            evidence,
            (list, tuple),
        ):
            raise TypeError(
                "evidence must be a list or tuple."
            )

        for item in evidence:
            if not isinstance(
                item,
                GroundedEvidence,
            ):
                raise TypeError(
                    "evidence must contain "
                    "GroundedEvidence objects."
                )

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