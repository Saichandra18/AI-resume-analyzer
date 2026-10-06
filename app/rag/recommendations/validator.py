"""Validate that RAG recommendations remain grounded in evidence."""

from app.rag.models import GroundedEvidence
from app.rag.recommendations.claim_detector import (
    UnsupportedClaimDetector,
)


class RecommendationGroundingValidator:
    """Validate recommendation grounding and traceability."""

    def __init__(self, claim_detector=None):
        """Initialize the recommendation validator."""

        self.claim_detector = (
            claim_detector
            or UnsupportedClaimDetector()
        )

    def validate(self, recommendations, evidence):
        """Validate recommendations against grounded evidence."""

        if not isinstance(
            recommendations,
            (list, tuple),
        ):
            raise TypeError(
                "recommendations must be a list or tuple."
            )

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

        evidence_by_id = {
            item.evidence_id: item
            for item in evidence
        }

        for recommendation in recommendations:
            self._validate_recommendation(
                recommendation,
                evidence_by_id,
            )

        return True

    def _validate_recommendation(
        self,
        recommendation,
        evidence_by_id,
    ):
        """Validate a single recommendation."""

        if not isinstance(
            recommendation,
            dict,
        ):
            raise TypeError(
                "recommendations must contain dictionaries."
            )

        required_fields = (
            "type",
            "message",
            "evidence_id",
            "source_chunk_ids",
            "confidence",
        )

        for field in required_fields:
            if field not in recommendation:
                raise ValueError(
                    "Recommendation is missing required "
                    f"field: {field}."
                )

        evidence_id = recommendation[
            "evidence_id"
        ]

        if not isinstance(
            evidence_id,
            str,
        ):
            raise TypeError(
                "recommendation evidence_id must be a string."
            )

        evidence = evidence_by_id.get(
            evidence_id
        )

        if evidence is None:
            raise ValueError(
                "Recommendation references unknown evidence."
            )

        source_chunk_ids = recommendation[
            "source_chunk_ids"
        ]

        if not isinstance(
            source_chunk_ids,
            list,
        ):
            raise TypeError(
                "recommendation source_chunk_ids "
                "must be a list."
            )

        if not source_chunk_ids:
            raise ValueError(
                "Recommendation must reference "
                "at least one source chunk."
            )

        evidence_chunk_ids = set(
            evidence.source_chunk_ids
        )

        missing_chunk_ids = [
            chunk_id
            for chunk_id in source_chunk_ids
            if chunk_id not in evidence_chunk_ids
        ]

        if missing_chunk_ids:
            raise ValueError(
                "Recommendation references source chunks "
                "not present in its evidence."
            )

        message = recommendation[
            "message"
        ]

        if not isinstance(
            message,
            str,
        ):
            raise TypeError(
                "recommendation message must be a string."
            )

        if not message.strip():
            raise ValueError(
                "Recommendation message cannot be empty."
            )

        confidence = recommendation[
            "confidence"
        ]

        if not isinstance(
            confidence,
            (int, float),
        ):
            raise TypeError(
                "recommendation confidence must be numeric."
            )

        if not 0.0 <= confidence <= 1.0:
            raise ValueError(
                "recommendation confidence must be "
                "between 0.0 and 1.0."
            )

        if confidence != evidence.confidence:
            raise ValueError(
                "Recommendation confidence must match "
                "the supporting evidence confidence."
            )

        unsupported_terms = (
            self.claim_detector.detect(
                recommendation,
                evidence.text,
            )
        )

        if unsupported_terms:
            raise ValueError(
                "Recommendation contains unsupported "
                "claim terms: "
                + ", ".join(unsupported_terms)
            )