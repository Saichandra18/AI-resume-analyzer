import pytest

from app.rag.models import (
    GroundedEvidence,
    RetrievedChunk,
)
from app.rag.optimization.orchestrator import (
    RAGOptimizationOrchestrator,
)


class DummyRetriever:
    def __init__(self, chunks=None):
        self.chunks = chunks or []

    def retrieve(self, jd_analysis):
        return self.chunks


class DummyEvidenceBuilder:
    def __init__(self, evidence):
        self.evidence = evidence

    def build(self, retrieved_chunks):
        return self.evidence


class DummyRecommendationBuilder:
    def __init__(self):
        self.calls = []

    def build(self, evidence, requirements=None):
        self.calls.append(
            {
                "evidence": evidence,
                "requirements": requirements,
            }
        )

        return [
            {
                "category": "skill",
                "value": "Python",
                "evidence_id": "evidence:0",
                "source_chunk_ids": ["doc:0"],
                "confidence": 0.9,
                "metadata": {"document_id": "doc"},
            }
        ]


class DummySafetyFilter:
    def __init__(self):
        self.calls = []

    def filter(self, recommendations, evidence):
        self.calls.append(
            {
                "recommendations": recommendations,
                "evidence": evidence,
            }
        )

        return (
            recommendations,
            [],
        )


class DummySignalSet:
    def __init__(self):
        self.signals = ["signal"]
        self.metadata = {}


class DummySignalMapper:
    def __init__(self):
        self.calls = []

    def map(self, recommendations, metadata=None):
        self.calls.append(
            {
                "recommendations": recommendations,
                "metadata": metadata,
            }
        )

        return DummySignalSet()


class DummySignalValidator:
    def __init__(self):
        self.calls = []

    def validate(
        self,
        signal_set,
        evidence,
        retrieved_chunks,
    ):
        self.calls.append(
            {
                "signal_set": signal_set,
                "evidence": evidence,
                "retrieved_chunks": retrieved_chunks,
            }
        )

        return True


class DummyPhase11Adapter:
    def __init__(self):
        self.calls = []

    def adapt(self, signal_set):
        self.calls.append(signal_set)

        return {
            "skills_to_emphasize": ["Python"],
        }


def make_chunk():
    return RetrievedChunk(
        chunk_id="doc:0",
        document_id="doc",
        text="Python experience",
        score=0.9,
        metadata={"document_id": "doc"},
    )


def make_evidence():
    return GroundedEvidence(
        evidence_id="evidence:0",
        text="Python experience",
        source_chunk_ids=["doc:0"],
        claim="Python",
        confidence=0.9,
        metadata={"document_id": "doc"},
    )


def make_orchestrator():
    retriever = DummyRetriever(
        chunks=[make_chunk()]
    )

    evidence_builder = DummyEvidenceBuilder(
        evidence=[make_evidence()]
    )

    recommendation_builder = (
        DummyRecommendationBuilder()
    )

    safety_filter = DummySafetyFilter()
    signal_mapper = DummySignalMapper()
    signal_validator = DummySignalValidator()
    phase11_adapter = DummyPhase11Adapter()

    orchestrator = RAGOptimizationOrchestrator(
        retriever=retriever,
        evidence_builder=evidence_builder,
        recommendation_builder=recommendation_builder,
        safety_filter=safety_filter,
        signal_mapper=signal_mapper,
        signal_validator=signal_validator,
        phase11_adapter=phase11_adapter,
    )

    return (
        orchestrator,
        recommendation_builder,
        safety_filter,
        signal_mapper,
        signal_validator,
        phase11_adapter,
    )


def test_runs_complete_optimization_flow():
    (
        orchestrator,
        recommendation_builder,
        safety_filter,
        signal_mapper,
        signal_validator,
        phase11_adapter,
    ) = make_orchestrator()

    result = orchestrator.optimize(
        {
            "required_skills": ["Python"],
        }
    )

    assert len(result["retrieved_chunks"]) == 1
    assert len(result["evidence"]) == 1
    assert len(result["recommendations"]) == 1
    assert len(result["safety_results"]) == 0
    assert result["phase11_payload"] == {
        "skills_to_emphasize": ["Python"]
    }

    assert len(recommendation_builder.calls) == 1
    assert len(safety_filter.calls) == 1
    assert len(signal_mapper.calls) == 1
    assert len(signal_validator.calls) == 1
    assert len(phase11_adapter.calls) == 1


def test_passes_jd_requirements_to_recommendation_builder():
    (
        orchestrator,
        recommendation_builder,
        _,
        _,
        _,
        _,
    ) = make_orchestrator()

    jd_analysis = {
        "required_skills": ["Python"],
        "technical_keywords": ["REST API"],
        "tools": ["Docker"],
    }

    orchestrator.optimize(jd_analysis)

    requirements = (
        recommendation_builder.calls[0][
            "requirements"
        ]
    )

    assert requirements == [
        "Python",
        "REST API",
        "Docker",
    ]


def test_extracts_all_supported_requirement_fields():
    requirements = (
        RAGOptimizationOrchestrator
        ._extract_requirements(
            {
                "required_skills": ["Python"],
                "technical_keywords": ["SQL"],
                "responsibilities": [
                    "Build APIs"
                ],
                "domain_knowledge": [
                    "cloud"
                ],
                "tools": ["Docker"],
                "experience_requirements": [
                    "3 years"
                ],
            }
        )
    )

    assert requirements == [
        "Python",
        "SQL",
        "Build APIs",
        "cloud",
        "Docker",
        "3 years",
    ]


def test_accepts_scalar_requirement_values():
    requirements = (
        RAGOptimizationOrchestrator
        ._extract_requirements(
            {
                "required_skills": "Python",
                "tools": "Docker",
            }
        )
    )

    assert requirements == [
        "Python",
        "Docker",
    ]


def test_ignores_missing_requirement_fields():
    requirements = (
        RAGOptimizationOrchestrator
        ._extract_requirements(
            {
                "required_skills": ["Python"],
            }
        )
    )

    assert requirements == ["Python"]


def test_preserves_jd_analysis_in_signal_metadata():
    (
        orchestrator,
        _,
        _,
        signal_mapper,
        _,
        _,
    ) = make_orchestrator()

    jd_analysis = {
        "required_skills": ["Python"],
        "job_title": "Backend Engineer",
    }

    orchestrator.optimize(jd_analysis)

    metadata = signal_mapper.calls[0][
        "metadata"
    ]

    assert metadata["jd_analysis"] == jd_analysis
    assert metadata["retrieved_chunk_count"] == 1
    assert metadata["evidence_count"] == 1
    assert metadata["recommendation_count"] == 1


def test_returns_expected_metadata_counts():
    orchestrator, *_ = make_orchestrator()

    result = orchestrator.optimize(
        {
            "required_skills": ["Python"],
        }
    )

    assert result["metadata"] == {
        "retrieved_chunk_count": 1,
        "evidence_count": 1,
        "recommendation_count": 1,
        "signal_count": 1,
    }


def test_rejects_missing_retriever():
    with pytest.raises(
        ValueError,
        match="retriever is required",
    ):
        RAGOptimizationOrchestrator(
            retriever=None
        )


def test_rejects_invalid_retriever():
    with pytest.raises(
        TypeError,
        match="retrieve method",
    ):
        RAGOptimizationOrchestrator(
            retriever=object()
        )


def test_rejects_missing_jd_analysis():
    orchestrator, *_ = make_orchestrator()

    with pytest.raises(
        ValueError,
        match="jd_analysis is required",
    ):
        orchestrator.optimize(None)


def test_rejects_invalid_jd_analysis():
    orchestrator, *_ = make_orchestrator()

    with pytest.raises(
        TypeError,
        match="jd_analysis must be a dictionary",
    ):
        orchestrator.optimize(
            ["Python"]
        )


def test_rejects_invalid_retriever_result():
    class InvalidRetriever:
        def retrieve(self, jd_analysis):
            return "invalid"

    orchestrator = RAGOptimizationOrchestrator(
        retriever=InvalidRetriever()
    )

    with pytest.raises(
        TypeError,
        match="retriever must return",
    ):
        orchestrator.optimize(
            {"required_skills": ["Python"]}
        )


def test_does_not_mutate_jd_analysis():
    (
        orchestrator,
        _,
        _,
        _,
        _,
        _,
    ) = make_orchestrator()

    jd_analysis = {
        "required_skills": ["Python"],
        "nested": {
            "value": "original"
        },
    }

    original = {
        "required_skills": ["Python"],
        "nested": {
            "value": "original"
        },
    }

    orchestrator.optimize(jd_analysis)

    assert jd_analysis == original