import pytest

from app.rag.config import RAGConfig
from app.rag.embeddings.local import LocalEmbeddingProvider
from app.rag.models import DocumentChunk
from app.rag.optimization.service import RAGOptimizationService
from app.rag.vectorstore.in_memory import InMemoryVectorStore
from app.rag.vectorstore.registry import ChunkRegistry


class FakeOrchestrator:
    def __init__(self):
        self.calls = []

    def optimize(self, jd_analysis):
        self.calls.append(jd_analysis)
        return {
            "retrieved_chunks": [],
            "evidence": [],
            "recommendations": [],
            "safety_results": [],
            "signals": [],
            "phase11_payload": {},
            "metadata": {},
        }


def enabled_config():
    config = RAGConfig()
    config.enabled = True
    return config


def test_disabled_service_does_not_initialize_runtime(monkeypatch):
    monkeypatch.setenv("RAG_ENABLED", "false")

    service = RAGOptimizationService(
        config=RAGConfig()
    )

    assert service.embedding_provider is None
    assert service.vector_store is None
    assert service.chunk_registry is None
    assert service.retrieval_service is None
    assert service.retriever is None
    assert service.orchestrator is None


def test_enabled_service_initializes_runtime_dependencies():
    service = RAGOptimizationService(
        config=enabled_config()
    )

    assert service.embedding_provider is not None
    assert service.vector_store is not None
    assert service.chunk_registry is not None
    assert service.retrieval_service is not None
    assert service.retriever is not None
    assert service.orchestrator is not None


def test_runtime_dependencies_can_be_injected():
    embedding_provider = LocalEmbeddingProvider(dimension=16)
    vector_store = InMemoryVectorStore()
    chunk_registry = ChunkRegistry()
    orchestrator = FakeOrchestrator()

    service = RAGOptimizationService(
        config=enabled_config(),
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        chunk_registry=chunk_registry,
        orchestrator=orchestrator,
    )

    assert service.embedding_provider is embedding_provider
    assert service.vector_store is vector_store
    assert service.chunk_registry is chunk_registry
    assert service.orchestrator is orchestrator


def test_indexing_uses_service_runtime():
    service = RAGOptimizationService(
        config=enabled_config()
    )

    chunk = DocumentChunk(
        chunk_id="runtime-1",
        document_id="doc-1",
        text="Python Flask backend API development.",
        metadata={},
    )

    indexed_ids = service.index_chunks([chunk])

    assert indexed_ids == ["runtime-1"]
    assert service.count_indexed_chunks() == 1
    assert service.chunk_registry.get("runtime-1") is chunk


def test_indexed_chunks_remain_available_for_same_service():
    service = RAGOptimizationService(
        config=enabled_config()
    )

    chunk = DocumentChunk(
        chunk_id="runtime-2",
        document_id="doc-2",
        text="Machine learning model development.",
        metadata={},
    )

    service.index_chunks([chunk])

    assert service.vector_store.count() == 1
    assert service.chunk_registry.get("runtime-2") is not None


def test_count_indexed_chunks_disabled_returns_zero():
    service = RAGOptimizationService(
        config=RAGConfig()
    )

    assert service.count_indexed_chunks() == 0


def test_optimize_uses_injected_orchestrator():
    orchestrator = FakeOrchestrator()

    service = RAGOptimizationService(
        config=enabled_config(),
        orchestrator=orchestrator,
    )

    jd_analysis = {
        "required_skills": ["Python"],
    }

    result = service.optimize(jd_analysis)

    assert orchestrator.calls == [jd_analysis]
    assert result["metadata"]["rag_enabled"] is True


def test_optimize_rejects_invalid_orchestrator_result():
    class InvalidOrchestrator:
        def optimize(self, jd_analysis):
            return None

    service = RAGOptimizationService(
        config=enabled_config(),
        orchestrator=InvalidOrchestrator(),
    )

    with pytest.raises(TypeError):
        service.optimize({})