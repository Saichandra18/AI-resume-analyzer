import pytest

from app.rag.optimization.service import RAGOptimizationService


class FakeConfig:
    enabled = True


class FakeEmbeddingProvider:
    pass


class FakeVectorStore:
    pass


class FakeOrchestrator:
    def optimize(self, jd_analysis):
        return {
            "retrieved_chunks": [],
            "evidence": [],
            "recommendations": [],
            "safety_results": [],
            "signals": None,
            "phase11_payload": {
                "skills_to_emphasize": ["Python"],
                "experience_to_emphasize": [],
                "keywords_to_emphasize": [],
                "emphasis_instructions": [],
                "grounding": [],
                "metadata": {},
            },
            "metadata": {},
        }


def test_enabled_service_can_construct_default_orchestrator(monkeypatch):
    monkeypatch.setattr(
        "app.rag.optimization.service.RAGConfig",
        FakeConfig,
    )

    service = RAGOptimizationService()

    assert service.enabled is True
    assert service.orchestrator is not None
    assert hasattr(service.orchestrator, "optimize")


def test_disabled_service_does_not_require_rag_dependencies(monkeypatch):
    class DisabledConfig:
        enabled = False

    monkeypatch.setattr(
        "app.rag.optimization.service.RAGConfig",
        DisabledConfig,
    )

    service = RAGOptimizationService()

    assert service.enabled is False
    assert service.orchestrator is None


def test_explicit_orchestrator_is_preserved():
    orchestrator = FakeOrchestrator()

    service = RAGOptimizationService(
        orchestrator=orchestrator,
        config=FakeConfig(),
    )

    assert service.orchestrator is orchestrator


def test_explicit_orchestrator_overrides_default_wiring():
    orchestrator = FakeOrchestrator()

    service = RAGOptimizationService(
        orchestrator=orchestrator,
        config=FakeConfig(),
    )

    assert service.orchestrator is orchestrator


def test_enabled_service_returns_default_rag_payload(monkeypatch):
    monkeypatch.setattr(
        "app.rag.optimization.service.RAGConfig",
        FakeConfig,
    )

    service = RAGOptimizationService()

    result = service.optimize(
        {
            "required_skills": [],
            "qualifications": [],
            "experience": None,
            "keywords": [],
        }
    )

    assert isinstance(result, dict)
    assert "phase11_payload" in result
    assert isinstance(result["phase11_payload"], dict)


def test_service_wiring_does_not_change_disabled_payload(monkeypatch):
    class DisabledConfig:
        enabled = False

    monkeypatch.setattr(
        "app.rag.optimization.service.RAGConfig",
        DisabledConfig,
    )

    service = RAGOptimizationService()

    result = service.optimize(
        {
            "required_skills": ["Python"],
            "qualifications": [],
            "experience": None,
            "keywords": ["Python"],
        }
    )

    assert result["enabled"] is False
    assert result["retrieved_chunks"] == []
    assert result["evidence"] == []
    assert result["recommendations"] == []
    assert result["safety_results"] == []
    assert result["signals"] is None


def test_invalid_default_wiring_is_rejected(monkeypatch):
    class BrokenConfig:
        enabled = True

    monkeypatch.setattr(
        "app.rag.optimization.service.RAGConfig",
        BrokenConfig,
    )

    monkeypatch.setattr(
        "app.rag.optimization.service.RAGOptimizationOrchestrator",
        lambda *args, **kwargs: None,
    )

    with pytest.raises(TypeError):
        RAGOptimizationService()