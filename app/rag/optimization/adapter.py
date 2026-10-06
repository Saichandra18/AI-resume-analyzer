"""Adapt RAG optimization context for resume optimization."""

from copy import deepcopy

from app.rag.models import RAGContext


class RAGOptimizationAdapter:
    """Convert RAG context into a Phase-11-compatible payload."""

    def adapt(self, context):
        """Create an advisory optimization payload from RAG context."""

        if not isinstance(context, RAGContext):
            raise TypeError(
                "context must be a RAGContext object."
            )

        recommendations = deepcopy(
            context.recommendations
        )

        evidence = [
            {
                "evidence_id": item.evidence_id,
                "text": item.text,
                "claim": item.claim,
                "confidence": item.confidence,
                "source_chunk_ids": list(
                    item.source_chunk_ids
                ),
                "metadata": deepcopy(
                    item.metadata
                ),
            }
            for item in context.evidence
        ]

        skills_to_emphasize = (
            self._extract_terms(
                recommendations,
                "skill",
            )
        )

        experience_to_emphasize = (
            self._extract_terms(
                recommendations,
                "experience",
            )
        )

        return {
            "skills_to_emphasize": (
                skills_to_emphasize
            ),
            "experience_to_emphasize": (
                experience_to_emphasize
            ),
            "evidence": evidence,
            "recommendations": recommendations,
            "metadata": deepcopy(
                context.metadata
            ),
        }

    @staticmethod
    def _extract_terms(
        recommendations,
        category,
    ):
        """Extract explicitly categorized recommendation terms."""

        terms = []

        for recommendation in recommendations:
            if not isinstance(
                recommendation,
                dict,
            ):
                continue

            recommendation_category = (
                recommendation.get("category")
            )

            if recommendation_category != category:
                continue

            value = recommendation.get(
                "value"
            )

            if value is None:
                continue

            if isinstance(
                value,
                (list, tuple),
            ):
                values = value
            else:
                values = [value]

            for item in values:
                normalized = " ".join(
                    str(item).split()
                )

                if normalized and normalized not in terms:
                    terms.append(normalized)

        return terms