"""Integration tests for resume-aware RAG optimization."""

from copy import deepcopy

from app.rag.models import RetrievedChunk
from app.rag.optimization.orchestrator import (
    RAGOptimizationOrchestrator,
)
from app.rag.optimization.signals import (
    OptimizationSignalSet,
)


class FakeRetriever:
    """Return deterministic retrieved chunks."""

    def __init__(self):
        self.calls = []

    def retrieve(self, jd_analysis, resume_context=None):
        self.calls.append(
            {
                "jd_analysis": deepcopy(jd_analysis),
                "resume_context": deepcopy(resume_context),
            }
        )

        return [
            RetrievedChunk(
                chunk_id="chunk-1",
                text="Python and machine learning experience.",
                score=0.95,
                document_id="doc-1",
                metadata={},
            )
        ]


class FakeEvidenceBuilder:
    """Build deterministic grounded evidence."""

    def build(self, retrieved_chunks, requirements=None):
        return []


class FakeRecommendationBuilder:
    """Build no recommendations for this integration test."""

    def build(self, evidence, requirements=None):
        return []


class FakeSafetyFilter:
    """Allow all recommendations."""

    def filter(self, recommendations, evidence):
        return recommendations, []


class FakeSignalMapper:
    """Return the same signal-set type used by production."""

    def map(self, recommendations, metadata=None):
        return OptimizationSignalSet(
            signals=[]
        )


class FakeSignalValidator:
    """Accept the mapped signals."""

    def validate(
        self,
        signals,
        evidence,
        retrieved_chunks,
    ):
        return True


class FakePhase11Adapter:
    """Return a deterministic Phase 11 payload."""

    def adapt(self, signals):
        return {
            "skills_to_emphasize": [],
            "experience_to_emphasize": [],
            "keywords_to_emphasize": [],
            "emphasis_instructions": [],
        }


def _build_orchestrator():
    """Build an orchestrator with deterministic dependencies."""

    return RAGOptimizationOrchestrator(
        retriever=FakeRetriever(),
        evidence_builder=FakeEvidenceBuilder(),
        recommendation_builder=FakeRecommendationBuilder(),
        safety_filter=FakeSafetyFilter(),
        signal_mapper=FakeSignalMapper(),
        signal_validator=FakeSignalValidator(),
        phase11_adapter=FakePhase11Adapter(),
    )


def _jd_analysis():
    """Return representative JD analysis."""

    return {
        "cleaned_text": "Python machine learning engineer",
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
                "description": "Built ML applications.",
            }
        ],
        "projects": [
            {
                "name": "AI Resume Analyzer",
            }
        ],
        "education": [
            "B.Tech",
        ],
        "certifications": [],
    }


def test_orchestrator_passes_resume_context_to_retriever():
    """Resume context should reach the retrieval layer."""

    orchestrator = _build_orchestrator()

    result = orchestrator.optimize(
        _jd_analysis(),
        resume_context=_resume_context(),
    )

    retriever = orchestrator.retriever

    assert len(retriever.calls) == 1
    assert (
        retriever.calls[0]["resume_context"]
        == _resume_context()
    )
    assert result["retrieved_chunks"]


def test_orchestrator_passes_jd_analysis_unchanged():
    """Existing JD analysis must remain unchanged."""

    orchestrator = _build_orchestrator()
    jd_analysis = _jd_analysis()

    orchestrator.optimize(
        jd_analysis,
        resume_context=_resume_context(),
    )

    assert (
        orchestrator.retriever.calls[0]["jd_analysis"]
        == jd_analysis
    )


def test_orchestrator_does_not_mutate_resume_context():
    """Resume context must not be modified by optimization."""

    orchestrator = _build_orchestrator()

    resume_context = _resume_context()
    original = deepcopy(resume_context)

    orchestrator.optimize(
        _jd_analysis(),
        resume_context=resume_context,
    )

    assert resume_context == original


def test_orchestrator_without_resume_context_remains_compatible():
    """Optimization should still work without resume context."""

    orchestrator = _build_orchestrator()

    result = orchestrator.optimize(
        _jd_analysis()
    )

    assert result["retrieved_chunks"]
    assert (
        orchestrator.retriever.calls[0]["resume_context"]
        is None
    )


def test_orchestrator_returns_phase11_payload():
    """The orchestrator should continue producing a Phase 11 payload."""

    orchestrator = _build_orchestrator()

    result = orchestrator.optimize(
        _jd_analysis(),
        resume_context=_resume_context(),
    )

    assert "phase11_payload" in result
    assert (
        result["phase11_payload"]["skills_to_emphasize"]
        == []
    )
    assert (
        result["phase11_payload"]["experience_to_emphasize"]
        == []
    )
    assert (
        result["phase11_payload"]["keywords_to_emphasize"]
        == []
    )
    assert (
        result["phase11_payload"]["emphasis_instructions"]
        == []
    )


def test_orchestrator_reports_resume_context_availability():
    """Resume context availability should be tracked internally."""

    orchestrator = _build_orchestrator()

    result = orchestrator.optimize(
        _jd_analysis(),
        resume_context=_resume_context(),
    )

    assert result["metadata"]["retrieved_chunk_count"] == 1
    assert result["metadata"]["evidence_count"] == 0
    assert result["metadata"]["recommendation_count"] == 0