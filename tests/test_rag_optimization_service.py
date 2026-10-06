"""Tests for the RAG optimization service."""

import pytest

from app.rag.knowledge.service import KnowledgeBaseService
from app.rag.models import RetrievedChunk
from app.rag.optimization.service import RAGOptimizationService


class FakeConfig:
    """Minimal configuration for service tests."""

    def __init__(self, enabled=False):
        self.enabled = enabled


class FakeOrchestrator:
    """Minimal orchestrator for service tests."""

    def __init__(self, result=None):
        self.result = result
        self.calls = []

    def optimize(self, jd_analysis):
        self.calls.append(jd_analysis)
        return self.result


class FakeKnowledgeBaseService:
    """Minimal knowledge-base service for service tests."""

    def __init__(self, results=None, indexed_count=0):
        self.results = results or []
        self._indexed_count = indexed_count
        self.calls = []

    def retrieve(self, jd_analysis):
        self.calls.append(jd_analysis)
        return self.results

    def indexed_count(self):
        return self._indexed_count


def make_result():
    """Build a representative orchestrator result."""

    return {
        "retrieved_chunks": ["chunk"],
        "evidence": ["evidence"],
        "recommendations": ["recommendation"],
        "safety_results": ["safe"],
        "signals": "signal-set",
        "phase11_payload": {
            "skills_to_emphasize": ["Python"],
            "experience_to_emphasize": [
                "API development"
            ],
            "keywords_to_emphasize": ["Flask"],
            "emphasis_instructions": [
                "Emphasize backend development."
            ],
            "grounding": [
                {
                    "evidence_id": "evidence:0",
                }
            ],
            "metadata": {
                "source": "rag",
            },
        },
        "metadata": {
            "signal_count": 1,
        },
    }


def make_knowledge_chunk(
    chunk_id="knowledge-1",
    document_id="ats-guidelines",
    text="General optimization guidance.",
    score=0.9,
    category="ats",
):
    """Build a valid RetrievedChunk for knowledge tests."""

    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id=document_id,
        text=text,
        score=score,
        metadata={
            "source_category": category,
        },
    )


def test_service_requires_jd_analysis():
    """Service should reject missing JD analysis."""

    service = RAGOptimizationService(
        config=FakeConfig(enabled=False)
    )

    with pytest.raises(ValueError):
        service.optimize(None)


def test_service_requires_dictionary_jd_analysis():
    """Service should reject non-dictionary JD analysis."""

    service = RAGOptimizationService(
        config=FakeConfig(enabled=False)
    )

    with pytest.raises(TypeError):
        service.optimize("invalid")


def test_disabled_service_does_not_require_orchestrator():
    """Disabled service should work without an orchestrator."""

    service = RAGOptimizationService(
        config=FakeConfig(enabled=False)
    )

    result = service.optimize(
        {"required_skills": ["Python"]}
    )

    assert result["enabled"] is False
    assert result["retrieved_chunks"] == []
    assert result["evidence"] == []
    assert result["recommendations"] == []
    assert result["safety_results"] == []
    assert result["signals"] is None


def test_disabled_service_returns_empty_phase11_payload():
    """Disabled service should return an empty Phase 11 payload."""

    service = RAGOptimizationService(
        config=FakeConfig(enabled=False)
    )

    payload = service.get_phase11_payload(
        {"required_skills": ["Python"]}
    )

    assert payload == {
        "skills_to_emphasize": [],
        "experience_to_emphasize": [],
        "keywords_to_emphasize": [],
        "emphasis_instructions": [],
        "grounding": [],
        "metadata": {
            "rag_enabled": False,
        },
    }


def test_disabled_service_does_not_call_orchestrator():
    """Disabled service should not call the orchestrator."""

    orchestrator = FakeOrchestrator(
        result=make_result()
    )

    service = RAGOptimizationService(
        orchestrator=orchestrator,
        config=FakeConfig(enabled=False),
    )

    service.optimize(
        {"required_skills": ["Python"]}
    )

    assert orchestrator.calls == []


def test_disabled_service_returns_empty_knowledge_context():
    """Disabled service should return empty knowledge context."""

    knowledge_service = FakeKnowledgeBaseService(
        results=[
            make_knowledge_chunk(
                text="knowledge"
            )
        ]
    )

    service = RAGOptimizationService(
        config=FakeConfig(enabled=False),
        knowledge_base_service=knowledge_service,
    )

    result = service.optimize(
        {"required_skills": ["Python"]}
    )

    assert result["knowledge_context"] == {
        "enabled": False,
        "retrieved_chunks": [],
        "count": 0,
        "metadata": {
            "knowledge_base": False,
            "indexed_count": 0,
        },
    }

    assert knowledge_service.calls == []


def test_enabled_service_constructs_default_orchestrator():
    """Enabled service should construct a default orchestrator."""

    service = RAGOptimizationService(
        config=FakeConfig(enabled=True)
    )

    assert service.orchestrator is not None
    assert hasattr(
        service.orchestrator,
        "optimize",
    )


def test_enabled_service_calls_orchestrator():
    """Enabled service should call the orchestrator."""

    orchestrator = FakeOrchestrator(
        result=make_result()
    )

    service = RAGOptimizationService(
        orchestrator=orchestrator,
        config=FakeConfig(enabled=True),
    )

    jd_analysis = {
        "required_skills": ["Python"],
        "technical_keywords": ["Flask"],
    }

    result = service.optimize(jd_analysis)

    assert len(orchestrator.calls) == 1
    assert orchestrator.calls[0] == jd_analysis
    assert result["enabled"] is True


def test_enabled_service_returns_orchestrator_result():
    """Service should preserve orchestrator result fields."""

    orchestrator = FakeOrchestrator(
        result=make_result()
    )

    service = RAGOptimizationService(
        orchestrator=orchestrator,
        config=FakeConfig(enabled=True),
    )

    result = service.optimize(
        {"required_skills": ["Python"]}
    )

    assert result["retrieved_chunks"] == ["chunk"]
    assert result["evidence"] == ["evidence"]
    assert result["recommendations"] == [
        "recommendation"
    ]
    assert result["signals"] == "signal-set"


def test_enabled_service_returns_phase11_payload():
    """Service should expose the Phase 11 payload."""

    orchestrator = FakeOrchestrator(
        result=make_result()
    )

    service = RAGOptimizationService(
        orchestrator=orchestrator,
        config=FakeConfig(enabled=True),
    )

    payload = service.get_phase11_payload(
        {"required_skills": ["Python"]}
    )

    assert payload["skills_to_emphasize"] == [
        "Python"
    ]

    assert payload["experience_to_emphasize"] == [
        "API development"
    ]

    assert payload["keywords_to_emphasize"] == [
        "Flask"
    ]


def test_phase11_payload_is_defensively_copied():
    """Phase 11 payload should be defensively copied."""

    orchestrator = FakeOrchestrator(
        result=make_result()
    )

    service = RAGOptimizationService(
        orchestrator=orchestrator,
        config=FakeConfig(enabled=True),
    )

    payload = service.get_phase11_payload(
        {"required_skills": ["Python"]}
    )

    payload["skills_to_emphasize"].append(
        "Docker"
    )

    second_payload = service.get_phase11_payload(
        {"required_skills": ["Python"]}
    )

    assert second_payload[
        "skills_to_emphasize"
    ] == ["Python"]


def test_enabled_service_rejects_invalid_orchestrator_result():
    """Service should reject an invalid orchestrator result."""

    orchestrator = FakeOrchestrator(
        result=None
    )

    service = RAGOptimizationService(
        orchestrator=orchestrator,
        config=FakeConfig(enabled=True),
    )

    with pytest.raises(TypeError):
        service.optimize(
            {"required_skills": ["Python"]}
        )


def test_enabled_service_rejects_missing_phase11_payload():
    """Service should reject results without Phase 11 payload."""

    orchestrator = FakeOrchestrator(
        result={
            "metadata": {},
        }
    )

    service = RAGOptimizationService(
        orchestrator=orchestrator,
        config=FakeConfig(enabled=True),
    )

    with pytest.raises(TypeError):
        service.optimize(
            {"required_skills": ["Python"]}
        )


def test_service_rejects_invalid_orchestrator():
    """Service should reject an invalid orchestrator."""

    with pytest.raises(TypeError):
        RAGOptimizationService(
            orchestrator=object(),
            config=FakeConfig(enabled=True),
        )


def test_service_defaults_to_rag_config(monkeypatch):
    """Service should use RAGConfig when no config is provided."""

    monkeypatch.setenv(
        "RAG_ENABLED",
        "false",
    )

    service = RAGOptimizationService()

    assert service.enabled is False


def test_service_reads_enabled_from_rag_config(monkeypatch):
    """Service should respect RAG_ENABLED configuration."""

    monkeypatch.setenv(
        "RAG_ENABLED",
        "true",
    )

    orchestrator = FakeOrchestrator(
        result=make_result()
    )

    service = RAGOptimizationService(
        orchestrator=orchestrator
    )

    assert service.enabled is True

    service.optimize(
        {"required_skills": ["Python"]}
    )

    assert len(orchestrator.calls) == 1


# ---------------------------------------------------------------------------
# Knowledge-base integration tests
# ---------------------------------------------------------------------------


def test_enabled_service_without_knowledge_service_returns_empty_context():
    """Enabled service without KB should expose empty KB context."""

    orchestrator = FakeOrchestrator(
        result=make_result()
    )

    service = RAGOptimizationService(
        orchestrator=orchestrator,
        config=FakeConfig(enabled=True),
    )

    result = service.optimize(
        {"required_skills": ["Python"]}
    )

    assert result["knowledge_context"] == {
        "enabled": False,
        "retrieved_chunks": [],
        "count": 0,
        "metadata": {
            "knowledge_base": False,
            "indexed_count": 0,
        },
    }


def test_enabled_service_retrieves_knowledge_context():
    """Service should retrieve and expose knowledge guidance."""

    orchestrator = FakeOrchestrator(
        result=make_result()
    )

    knowledge_chunks = [
        make_knowledge_chunk(
            chunk_id="knowledge-1",
            text="Use relevant keywords naturally.",
            category="ats",
        ),
        make_knowledge_chunk(
            chunk_id="knowledge-2",
            text=(
                "Keep resume formatting ATS-friendly."
            ),
            category="resume",
        ),
    ]

    knowledge_service = FakeKnowledgeBaseService(
        results=knowledge_chunks,
        indexed_count=17,
    )

    service = RAGOptimizationService(
        orchestrator=orchestrator,
        config=FakeConfig(enabled=True),
        knowledge_base_service=knowledge_service,
    )

    jd_analysis = {
        "required_skills": ["Python"],
        "keywords": ["Flask"],
    }

    result = service.optimize(jd_analysis)

    assert knowledge_service.calls == [
        jd_analysis
    ]

    context = result["knowledge_context"]

    assert context["enabled"] is True
    assert context["retrieved_chunks"] == (
        knowledge_chunks
    )
    assert context["count"] == 2

    assert context["metadata"] == {
        "knowledge_base": True,
        "indexed_count": 17,
        "guidance_count": 2,
    }

    assert len(context["guidance"]) == 2

    first_guidance = context["guidance"][0]

    assert first_guidance["text"] == (
        "Use relevant keywords naturally."
    )
    assert first_guidance["source_chunk_id"] == (
        "knowledge-1"
    )
    assert first_guidance["document_id"] == (
        "ats-guidelines"
    )
    assert first_guidance["score"] == 0.9
    assert first_guidance["category"] == "ats"

    second_guidance = context["guidance"][1]

    assert second_guidance["text"] == (
        "Keep resume formatting ATS-friendly."
    )
    assert second_guidance["source_chunk_id"] == (
        "knowledge-2"
    )
    assert second_guidance["category"] == "resume"


def test_knowledge_context_does_not_modify_candidate_evidence():
    """Knowledge guidance should not modify candidate evidence."""

    orchestrator = FakeOrchestrator(
        result=make_result()
    )

    knowledge_service = FakeKnowledgeBaseService(
        results=[
            make_knowledge_chunk(
                chunk_id="knowledge-evidence",
                text="General guidance",
            )
        ],
        indexed_count=5,
    )

    service = RAGOptimizationService(
        orchestrator=orchestrator,
        config=FakeConfig(enabled=True),
        knowledge_base_service=knowledge_service,
    )

    result = service.optimize(
        {"required_skills": ["Python"]}
    )

    assert result["evidence"] == [
        "evidence"
    ]

    assert result["recommendations"] == [
        "recommendation"
    ]

    assert result["signals"] == "signal-set"

    context = result["knowledge_context"]

    assert len(
        context["retrieved_chunks"]
    ) == 1

    assert context[
        "retrieved_chunks"
    ][0].text == "General guidance"

    assert context[
        "guidance"
    ][0]["text"] == "General guidance"


def test_knowledge_context_does_not_modify_phase11_payload():
    """Knowledge guidance should not modify Phase 11 output."""

    orchestrator = FakeOrchestrator(
        result=make_result()
    )

    knowledge_service = FakeKnowledgeBaseService(
        results=[
            make_knowledge_chunk(
                chunk_id="knowledge-phase11",
                text="ATS guidance",
            )
        ],
        indexed_count=10,
    )

    service = RAGOptimizationService(
        orchestrator=orchestrator,
        config=FakeConfig(enabled=True),
        knowledge_base_service=knowledge_service,
    )

    result = service.optimize(
        {"required_skills": ["Python"]}
    )

    assert result["phase11_payload"] == (
        make_result()["phase11_payload"]
    )


def test_service_rejects_invalid_knowledge_service():
    """Service should reject an invalid knowledge service."""

    orchestrator = FakeOrchestrator(
        result=make_result()
    )

    service = RAGOptimizationService(
        orchestrator=orchestrator,
        config=FakeConfig(enabled=True),
        knowledge_base_service=object(),
    )

    with pytest.raises(TypeError):
        service.optimize(
            {"required_skills": ["Python"]}
        )


def test_knowledge_context_is_defensively_copied():
    """Knowledge context should be isolated between calls."""

    orchestrator = FakeOrchestrator(
        result=make_result()
    )

    knowledge_service = FakeKnowledgeBaseService(
        results=[
            make_knowledge_chunk(
                chunk_id="knowledge-copy",
                text="guidance",
            )
        ],
        indexed_count=3,
    )

    service = RAGOptimizationService(
        orchestrator=orchestrator,
        config=FakeConfig(enabled=True),
        knowledge_base_service=knowledge_service,
    )

    result = service.optimize(
        {"required_skills": ["Python"]}
    )

    result[
        "knowledge_context"
    ][
        "retrieved_chunks"
    ].append("mutated")

    result[
        "knowledge_context"
    ][
        "guidance"
    ][0]["text"] = "mutated guidance"

    second_result = service.optimize(
        {"required_skills": ["Python"]}
    )

    second_context = second_result[
        "knowledge_context"
    ]

    assert len(
        second_context["retrieved_chunks"]
    ) == 1

    assert second_context[
        "retrieved_chunks"
    ][0].text == "guidance"

    assert second_context[
        "guidance"
    ][0]["text"] == "guidance"

    assert knowledge_service.results[
        0
    ].text == "guidance"


def test_knowledge_service_indexed_count_is_optional():
    """Knowledge service should work without indexed_count."""

    class MinimalKnowledgeService:
        """Minimal KB service without indexed_count."""

        def retrieve(self, jd_analysis):
            return [
                make_knowledge_chunk(
                    chunk_id="knowledge-minimal",
                    text="guidance",
                )
            ]

    orchestrator = FakeOrchestrator(
        result=make_result()
    )

    service = RAGOptimizationService(
        orchestrator=orchestrator,
        config=FakeConfig(enabled=True),
        knowledge_base_service=MinimalKnowledgeService(),
    )

    result = service.optimize(
        {"required_skills": ["Python"]}
    )

    context = result["knowledge_context"]

    assert len(
        context["retrieved_chunks"]
    ) == 1

    assert context[
        "retrieved_chunks"
    ][0].text == "guidance"

    assert context["count"] == 1

    assert context[
        "metadata"
    ]["indexed_count"] == 0

    assert context[
        "metadata"
    ]["knowledge_base"] is True

    assert context[
        "metadata"
    ]["guidance_count"] == 1


def test_optimization_service_integrates_real_knowledge_base():
    """Service should integrate with the real knowledge base."""

    knowledge_service = KnowledgeBaseService()
    knowledge_service.index_all()

    orchestrator = FakeOrchestrator(
        result=make_result()
    )

    service = RAGOptimizationService(
        orchestrator=orchestrator,
        config=FakeConfig(enabled=True),
        knowledge_base_service=knowledge_service,
    )

    jd_analysis = {
        "required_skills": [
            "Python",
            "SQL",
        ],
        "keywords": [
            "RAG",
            "LLM",
        ],
        "experience": [
            "2 years",
        ],
    }

    result = service.optimize(jd_analysis)

    knowledge_context = result[
        "knowledge_context"
    ]

    assert knowledge_context[
        "enabled"
    ] is True

    assert knowledge_context[
        "count"
    ] == 5

    assert knowledge_context[
        "metadata"
    ]["knowledge_base"] is True

    assert knowledge_context[
        "metadata"
    ]["indexed_count"] == 17

    assert knowledge_context[
        "metadata"
    ]["guidance_count"] == 5

    assert len(
        knowledge_context[
            "retrieved_chunks"
        ]
    ) == 5

    assert len(
        knowledge_context[
            "guidance"
        ]
    ) == 5

    assert all(
        isinstance(
            chunk,
            RetrievedChunk,
        )
        for chunk in knowledge_context[
            "retrieved_chunks"
        ]
    )

    assert all(
        hasattr(
            chunk,
            "chunk_id",
        )
        for chunk in knowledge_context[
            "retrieved_chunks"
        ]
    )

    assert all(
        hasattr(
            chunk,
            "text",
        )
        for chunk in knowledge_context[
            "retrieved_chunks"
        ]
    )


def test_real_knowledge_base_remains_separate_from_phase11():
    """Knowledge guidance should remain separate from Phase 11."""

    knowledge_service = KnowledgeBaseService()
    knowledge_service.index_all()

    orchestrator = FakeOrchestrator(
        result=make_result()
    )

    service = RAGOptimizationService(
        orchestrator=orchestrator,
        config=FakeConfig(enabled=True),
        knowledge_base_service=knowledge_service,
    )

    result = service.optimize(
        {
            "required_skills": ["Python"],
            "keywords": ["ATS", "RAG"],
        }
    )

    # Knowledge retrieval is exposed separately.
    assert result[
        "knowledge_context"
    ]["count"] == 5

    # Knowledge guidance is exposed separately.
    assert len(
        result[
            "knowledge_context"
        ]["guidance"]
    ) == 5

    # Candidate evidence remains whatever the
    # candidate/JD optimization orchestrator produced.
    assert result["evidence"] == [
        "evidence"
    ]

    # Candidate recommendations remain unchanged.
    assert result["recommendations"] == [
        "recommendation"
    ]

    # Knowledge guidance must not become
    # Phase 11 grounding.
    assert result[
        "phase11_payload"
    ]["grounding"] == [
        {
            "evidence_id": "evidence:0",
        }
    ]