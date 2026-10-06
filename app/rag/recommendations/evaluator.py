"""Evaluate the safety of RAG recommendations."""

from app.rag.models import GroundedEvidence
from app.rag.recommendations.claim_detector import (
    UnsupportedClaimDetector,
)
from app.rag.recommendations.safety import (
    RecommendationSafetyResult,
)


class RecommendationSafetyEvaluator:
    """Evaluate recommendations and return structured safety results."""

    def __init__(self, claim_detector=None):
        self.claim_detector = (
            claim_detector
            or UnsupportedClaimDetector()
        )

    def evaluate(self, recommendation, evidence):
        """Evaluate one recommendation against supporting evidence."""

        if not isinstance(recommendation, dict):
            raise TypeError(
                "recommendation must be a dictionary."
            )

        if not isinstance(evidence, GroundedEvidence):
            raise TypeError(
                "evidence must be a GroundedEvidence object."
            )

        evidence_id = recommendation.get(
            "evidence_id"
        )

        if evidence_id != evidence.evidence_id:
            return RecommendationSafetyResult(
                safe=False,
                recommendation=recommendation,
                reason=(
                    "Recommendation references "
                    "different evidence."
                ),
                evidence_id=evidence_id,
            )

        source_chunk_ids = recommendation.get(
            "source_chunk_ids"
        )

        if not isinstance(
            source_chunk_ids,
            list,
        ):
            raise TypeError(
                "recommendation source_chunk_ids "
                "must be a list."
            )

        if not source_chunk_ids:
            return RecommendationSafetyResult(
                safe=False,
                recommendation=recommendation,
                reason=(
                    "Recommendation must reference "
                    "at least one source chunk."
                ),
                evidence_id=evidence_id,
            )

        missing_chunk_ids = [
            chunk_id
            for chunk_id in source_chunk_ids
            if chunk_id not in evidence.source_chunk_ids
        ]

        if missing_chunk_ids:
            return RecommendationSafetyResult(
                safe=False,
                recommendation=recommendation,
                reason=(
                    "Recommendation references source "
                    "chunks not present in evidence."
                ),
                evidence_id=evidence_id,
                metadata={
                    "missing_chunk_ids": (
                        missing_chunk_ids
                    )
                },
            )

        message = recommendation.get("message")

        if not isinstance(message, str):
            raise TypeError(
                "recommendation message must be a string."
            )

        if not message.strip():
            return RecommendationSafetyResult(
                safe=False,
                recommendation=recommendation,
                reason=(
                    "Recommendation message "
                    "cannot be empty."
                ),
                evidence_id=evidence_id,
            )

        confidence = recommendation.get(
            "confidence"
        )

        if not isinstance(
            confidence,
            (int, float),
        ):
            raise TypeError(
                "recommendation confidence "
                "must be numeric."
            )

        if not 0.0 <= confidence <= 1.0:
            return RecommendationSafetyResult(
                safe=False,
                recommendation=recommendation,
                reason=(
                    "Recommendation confidence "
                    "must be between 0.0 and 1.0."
                ),
                evidence_id=evidence_id,
            )

        if confidence != evidence.confidence:
            return RecommendationSafetyResult(
                safe=False,
                recommendation=recommendation,
                reason=(
                    "Recommendation confidence must "
                    "match supporting evidence."
                ),
                evidence_id=evidence_id,
            )

        unsupported_terms = (
            self.claim_detector.detect(
                recommendation,
                evidence.text,
            )
        )

        if unsupported_terms:
            return RecommendationSafetyResult(
                safe=False,
                recommendation=recommendation,
                reason=(
                    "Recommendation contains "
                    "unsupported claim terms."
                ),
                unsupported_terms=unsupported_terms,
                evidence_id=evidence_id,
            )

        return RecommendationSafetyResult(
            safe=True,
            recommendation=recommendation,
            evidence_id=evidence_id,
            metadata={
                "validation": "grounded",
            },
        )