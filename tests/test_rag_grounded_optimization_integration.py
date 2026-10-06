"""Integration tests for grounded RAG optimization into Phase 11."""

from app.rag.models import (
    GroundedEvidence,
    RetrievedChunk,
)
from app.rag.optimization.orchestrator import (
    RAGOptimizationOrchestrator,
)
from app.rag.optimization.phase11_adapter import (
    Phase11OptimizationAdapter,
)
from app.rag.optimization.signal_mapper import (
    RecommendationSignalMapper,
)
from app.rag.optimization.signal_validator import (
    SignalGroundingValidator,
)
from app.rag.recommendations.filter import (
    SafeRecommendationFilter,
)


class FakeRetriever:
    """Return deterministic retrieved chunks."""

    def retrieve(self, jd_analysis, resume_context=None):
        return [
            RetrievedChunk(
                chunk_id="chunk-python",
                text="Python",
                score=0.98,
                document_id="resume-doc",
                metadata={
                    "section": "skills",
                },
            ),
            RetrievedChunk(
                chunk_id="chunk-ml",
                text="Machine learning",
                score=0.95,
                document_id="resume-doc",
                metadata={
                    "section": "projects",
                },
            ),
        ]


class FakeEvidenceBuilder:
    """Create deterministic grounded evidence."""

    def build(self, retrieved_chunks):
        return [
            GroundedEvidence(
                evidence_id="evidence-python",
                text="Python",
                claim="Python",
                source_chunk_ids=[
                    "chunk-python",
                ],
                confidence=0.98,
                metadata={
                    "section": "skills",
                },
            ),
            GroundedEvidence(
                evidence_id="evidence-ml",
                text="Machine learning",
                claim="Machine learning",
                source_chunk_ids=[
                    "chunk-ml",
                ],
                confidence=0.95,
                metadata={
                    "section": "projects",
                },
            ),
        ]


class GroundedRecommendationBuilder:
    """Return recommendations satisfying the safety contract."""

    def build(self, evidence, requirements=None):
        return [
            {
                "type": "emphasis",
                "message": "Python",
                "category": "skill",
                "value": "Python",
                "evidence_id": "evidence-python",
                "source_chunk_ids": [
                    "chunk-python",
                ],
                "confidence": 0.98,
                "metadata": {
                    "section": "skills",
                },
            },
            {
                "type": "emphasis",
                "message": "Machine learning",
                "category": "experience",
                "value": "Machine learning",
                "evidence_id": "evidence-ml",
                "source_chunk_ids": [
                    "chunk-ml",
                ],
                "confidence": 0.95,
                "metadata": {
                    "section": "projects",
                },
            },
        ]


def _build_orchestrator():
    """Build the orchestrator with deterministic components."""

    return RAGOptimizationOrchestrator(
        retriever=FakeRetriever(),
        evidence_builder=FakeEvidenceBuilder(),
        recommendation_builder=GroundedRecommendationBuilder(),
        safety_filter=SafeRecommendationFilter(),
        signal_mapper=RecommendationSignalMapper(),
        signal_validator=SignalGroundingValidator(),
        phase11_adapter=Phase11OptimizationAdapter(),
    )


def _jd_analysis():
    """Return a representative JD analysis."""

    return {
        "cleaned_text": (
            "Python machine learning engineer"
        ),
        "required_skills": [
            "Python",
            "Machine Learning",
        ],
        "qualifications": [],
        "experience": [],
        "keywords": [
            "machine learning",
        ],
    }


def _resume_context():
    """Return representative resume context."""

    return {
        "summary": "Python developer.",
        "skills": [
            "Python",
            "SQL",
        ],
        "experience": [
            {
                "role": "Python Developer",
                "description": (
                    "Built machine learning applications."
                ),
            }
        ],
        "projects": [
            {
                "name": "AI Resume Analyzer",
                "description": (
                    "Machine learning project."
                ),
            }
        ],
        "education": [
            "B.Tech",
        ],
        "certifications": [],
    }


def test_grounded_recommendations_are_produced():
    """Grounded evidence should produce recommendations."""

    orchestrator = _build_orchestrator()

    result = orchestrator.optimize(
        _jd_analysis(),
        resume_context=_resume_context(),
    )

    assert len(result["evidence"]) == 2
    assert len(result["recommendations"]) == 2


def test_grounded_recommendations_pass_safety_validation():
    """Supported recommendations should pass safety filtering."""

    orchestrator = _build_orchestrator()

    result = orchestrator.optimize(
        _jd_analysis(),
        resume_context=_resume_context(),
    )

    assert len(result["safety_results"]) == 2

    assert all(
        safety_result.safe
        for safety_result in result["safety_results"]
    )


def test_recommendations_are_converted_to_signals():
    """Safe recommendations should become optimization signals."""

    orchestrator = _build_orchestrator()

    result = orchestrator.optimize(
        _jd_analysis(),
        resume_context=_resume_context(),
    )

    signal_set = result["signals"]

    assert len(signal_set.signals) == 2

    signal_types = {
        signal.signal_type
        for signal in signal_set.signals
    }

    assert "skill" in signal_types
    assert "experience" in signal_types


def test_signals_are_grounded_in_retrieved_evidence():
    """Every generated signal must remain evidence-grounded."""

    orchestrator = _build_orchestrator()

    result = orchestrator.optimize(
        _jd_analysis(),
        resume_context=_resume_context(),
    )

    assert result["signals"].signals

    retrieved_ids = {
        chunk.chunk_id
        for chunk in result["retrieved_chunks"]
    }

    evidence_ids = {
        item.evidence_id
        for item in result["evidence"]
    }

    for signal in result["signals"].signals:
        assert signal.evidence_id in evidence_ids

        assert set(
            signal.source_chunk_ids
        ).issubset(retrieved_ids)


def test_phase11_payload_contains_grounded_optimization():
    """Grounded signals should reach the Phase 11 adapter."""

    orchestrator = _build_orchestrator()

    result = orchestrator.optimize(
        _jd_analysis(),
        resume_context=_resume_context(),
    )

    payload = result["phase11_payload"]

    assert "skills_to_emphasize" in payload
    assert "experience_to_emphasize" in payload
    assert "keywords_to_emphasize" in payload
    assert "emphasis_instructions" in payload

    assert "Python" in payload["skills_to_emphasize"]

    assert (
        "Machine learning"
        in payload["experience_to_emphasize"]
    )


def test_resume_context_does_not_create_unsupported_claims():
    """Optimization should only use claims supported by evidence."""

    orchestrator = _build_orchestrator()

    result = orchestrator.optimize(
        _jd_analysis(),
        resume_context=_resume_context(),
    )

    recommendation_text = " ".join(
        recommendation["message"]
        for recommendation in result["recommendations"]
    )

    assert "Python" in recommendation_text
    assert "Machine learning" in recommendation_text

    assert "Java" not in recommendation_text
    assert "AWS" not in recommendation_text
    assert "Kubernetes" not in recommendation_text