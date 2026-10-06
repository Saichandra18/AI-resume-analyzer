"""Filter RAG recommendations using safety evaluation."""

from app.rag.models import GroundedEvidence
from app.rag.recommendations.evaluator import (
    RecommendationSafetyEvaluator,
)


class SafeRecommendationFilter:
    """Keep only recommendations that pass safety evaluation."""

    def __init__(self, evaluator=None):
        self.evaluator = (
            evaluator
            or RecommendationSafetyEvaluator()
        )

    def filter(self, recommendations, evidence):
        """Return safe recommendations and safety results."""

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

        safe_recommendations = []
        safety_results = []

        for recommendation in recommendations:
            if not isinstance(
                recommendation,
                dict,
            ):
                raise TypeError(
                    "recommendations must contain "
                    "dictionaries."
                )

            evidence_id = recommendation.get(
                "evidence_id"
            )

            supporting_evidence = evidence_by_id.get(
                evidence_id
            )

            if supporting_evidence is None:
                raise ValueError(
                    "Recommendation references unknown "
                    "evidence."
                )

            result = self.evaluator.evaluate(
                recommendation,
                supporting_evidence,
            )

            safety_results.append(result)

            if result.safe:
                safe_recommendations.append(
                    recommendation
                )

        return (
            safe_recommendations,
            safety_results,
        )