"""Build RAG context for resume optimization."""

from copy import deepcopy

from app.rag.models import (
    GroundedEvidence,
    RAGContext,
    RetrievedChunk,
)
from app.rag.recommendations.safety import (
    RecommendationSafetyResult,
)


class OptimizationRAGContextBuilder:
    """Build safe RAG context for resume optimization."""

    def build(
        self,
        jd_analysis,
        retrieved_chunks,
        evidence,
        recommendations,
        safety_results=None,
        metadata=None,
    ):
        """Build optimization context from RAG outputs."""

        if not isinstance(jd_analysis, dict):
            raise TypeError(
                "jd_analysis must be a dictionary."
            )

        if not isinstance(
            retrieved_chunks,
            (list, tuple),
        ):
            raise TypeError(
                "retrieved_chunks must be a list or tuple."
            )

        if not isinstance(
            evidence,
            (list, tuple),
        ):
            raise TypeError(
                "evidence must be a list or tuple."
            )

        if not isinstance(
            recommendations,
            (list, tuple),
        ):
            raise TypeError(
                "recommendations must be a list or tuple."
            )

        if safety_results is not None and not isinstance(
            safety_results,
            (list, tuple),
        ):
            raise TypeError(
                "safety_results must be a list or tuple."
            )

        if metadata is not None and not isinstance(
            metadata,
            dict,
        ):
            raise TypeError(
                "metadata must be a dictionary."
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

        for item in evidence:
            if not isinstance(
                item,
                GroundedEvidence,
            ):
                raise TypeError(
                    "evidence must contain "
                    "GroundedEvidence objects."
                )

        for recommendation in recommendations:
            if not isinstance(
                recommendation,
                dict,
            ):
                raise TypeError(
                    "recommendations must contain "
                    "dictionaries."
                )

        if safety_results is not None:
            for result in safety_results:
                if not isinstance(
                    result,
                    RecommendationSafetyResult,
                ):
                    raise TypeError(
                        "safety_results must contain "
                        "RecommendationSafetyResult objects."
                    )

        safe_recommendations = (
            self._select_safe_recommendations(
                recommendations,
                safety_results,
            )
        )

        context_metadata = deepcopy(
            metadata or {}
        )

        context_metadata[
            "jd_analysis"
        ] = deepcopy(jd_analysis)

        context_metadata[
            "recommendation_count"
        ] = len(safe_recommendations)

        context_metadata[
            "evidence_count"
        ] = len(evidence)

        return RAGContext(
            retrieved_chunks=list(
                retrieved_chunks
            ),
            evidence=list(evidence),
            recommendations=deepcopy(
                safe_recommendations
            ),
            metadata=context_metadata,
        )

    @staticmethod
    def _select_safe_recommendations(
        recommendations,
        safety_results,
    ):
        """Select recommendations that passed safety checks."""

        if safety_results is None:
            return list(recommendations)

        safe_evidence_ids = {
            result.evidence_id
            for result in safety_results
            if result.safe
        }

        return [
            recommendation
            for recommendation in recommendations
            if recommendation.get(
                "evidence_id"
            ) in safe_evidence_ids
        ]