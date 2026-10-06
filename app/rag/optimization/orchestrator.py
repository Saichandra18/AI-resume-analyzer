"""Coordinate RAG optimization into a Phase 11 payload."""

from copy import deepcopy

from app.rag.grounding.evidence import EvidenceBuilder
from app.rag.optimization.phase11_adapter import (
    Phase11OptimizationAdapter,
)
from app.rag.optimization.signal_mapper import (
    RecommendationSignalMapper,
)
from app.rag.optimization.signal_validator import (
    SignalGroundingValidator,
)
from app.rag.recommendations.builder import RecommendationBuilder
from app.rag.recommendations.filter import SafeRecommendationFilter


class RAGOptimizationOrchestrator:
    """Coordinate grounded RAG optimization for Phase 11."""

    def __init__(
        self,
        retriever,
        evidence_builder=None,
        recommendation_builder=None,
        safety_filter=None,
        signal_mapper=None,
        signal_validator=None,
        phase11_adapter=None,
    ):
        if retriever is None:
            raise ValueError(
                "retriever is required"
            )

        if not hasattr(retriever, "retrieve"):
            raise TypeError(
                "retriever must provide a retrieve method"
            )

        self.retriever = retriever

        self.evidence_builder = (
            evidence_builder
            or EvidenceBuilder()
        )

        self.recommendation_builder = (
            recommendation_builder
            or RecommendationBuilder()
        )

        self.safety_filter = (
            safety_filter
            or SafeRecommendationFilter()
        )

        self.signal_mapper = (
            signal_mapper
            or RecommendationSignalMapper()
        )

        self.signal_validator = (
            signal_validator
            or SignalGroundingValidator()
        )

        self.phase11_adapter = (
            phase11_adapter
            or Phase11OptimizationAdapter()
        )

    def optimize(
        self,
        jd_analysis,
        resume_context=None,
    ):
        """Run the complete grounded RAG optimization flow."""

        if jd_analysis is None:
            raise ValueError(
                "jd_analysis is required"
            )

        if not isinstance(
            jd_analysis,
            dict,
        ):
            raise TypeError(
                "jd_analysis must be a dictionary"
            )

        if resume_context is not None and not isinstance(
            resume_context,
            dict,
        ):
            raise TypeError(
                "resume_context must be a dictionary."
            )

        # -------------------------------------------------
        # Resume-aware retrieval
        # -------------------------------------------------
        if resume_context is None:
            retrieved_chunks = self.retriever.retrieve(
                jd_analysis
            )
        else:
            try:
                retrieved_chunks = self.retriever.retrieve(
                    jd_analysis,
                    resume_context=resume_context,
                )
            except TypeError as exc:
                # Preserve compatibility with injected/legacy
                # retrievers that only accept jd_analysis.
                if "resume_context" not in str(exc):
                    raise

                retrieved_chunks = self.retriever.retrieve(
                    jd_analysis
                )

        if not isinstance(
            retrieved_chunks,
            (list, tuple),
        ):
            raise TypeError(
                "retriever must return a list or tuple"
            )

        evidence = self.evidence_builder.build(
            retrieved_chunks
        )

        requirements = self._extract_requirements(
            jd_analysis
        )

        recommendations = (
            self.recommendation_builder.build(
                evidence,
                requirements=requirements,
            )
        )

        (
            safe_recommendations,
            safety_results,
        ) = self.safety_filter.filter(
            recommendations,
            evidence,
        )

        signal_metadata = {
            "jd_analysis": deepcopy(
                jd_analysis
            ),
            "retrieved_chunk_count": len(
                retrieved_chunks
            ),
            "evidence_count": len(
                evidence
            ),
            "recommendation_count": len(
                safe_recommendations
            ),
            "resume_context_available": (
                resume_context is not None
            ),
        }

        if resume_context is not None:
            signal_metadata[
                "resume_context"
            ] = deepcopy(
                resume_context
            )

        signal_set = self.signal_mapper.map(
            safe_recommendations,
            metadata=signal_metadata,
        )

        self.signal_validator.validate(
            signal_set,
            evidence,
            retrieved_chunks,
        )

        phase11_payload = (
            self.phase11_adapter.adapt(
                signal_set
            )
        )

        return {
            "retrieved_chunks": retrieved_chunks,
            "evidence": evidence,
            "recommendations": safe_recommendations,
            "safety_results": safety_results,
            "signals": signal_set,
            "phase11_payload": phase11_payload,
            "metadata": {
                "retrieved_chunk_count": len(
                    retrieved_chunks
                ),
                "evidence_count": len(
                    evidence
                ),
                "recommendation_count": len(
                    safe_recommendations
                ),
                "signal_count": len(
                    signal_set.signals
                ),
            },
        }

    @staticmethod
    def _extract_requirements(jd_analysis):
        """Extract JD requirements for recommendation matching."""

        requirement_fields = (
            "required_skills",
            "technical_keywords",
            "responsibilities",
            "domain_knowledge",
            "tools",
            "experience_requirements",
        )

        requirements = []

        for field_name in requirement_fields:
            values = jd_analysis.get(
                field_name
            )

            if values is None:
                continue

            if isinstance(
                values,
                (list, tuple),
            ):
                requirements.extend(values)
            else:
                requirements.append(values)

        return requirements