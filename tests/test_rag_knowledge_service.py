from pathlib import Path

from app.rag.knowledge.service import KnowledgeBaseService


def test_service_initializes_default_dependencies():
    service = KnowledgeBaseService()

    assert service.embedding_provider is not None
    assert service.vector_store is not None
    assert service.chunk_registry is not None
    assert service.retrieval_service is not None
    assert service.catalog is not None
    assert service.indexing_pipeline is not None
    assert service.persistence is not None
    assert service.retriever is not None


def test_service_starts_with_empty_index():
    service = KnowledgeBaseService()

    assert service.indexed_count() == 0
    assert service.is_indexed() is False


def test_service_index_all_indexes_all_sources():
    service = KnowledgeBaseService()

    result = service.index_all()

    assert len(result) == 3
    assert service.indexed_count() == 17
    assert [item["source_id"] for item in result] == [
        "ats-guidelines",
        "resume-guidelines",
        "role-guidelines",
    ]


def test_service_indexes_expected_chunk_counts():
    service = KnowledgeBaseService()

    result = service.index_all()

    assert [item["chunk_count"] for item in result] == [
        4,
        6,
        7,
    ]


def test_service_can_index_single_source():
    service = KnowledgeBaseService()

    result = service.index_source("ats-guidelines")

    assert result["source_id"] == "ats-guidelines"
    assert result["chunk_count"] == 4
    assert service.indexed_count() == 4


def test_service_retrieves_knowledge():
    service = KnowledgeBaseService()
    service.index_all()

    results = service.retrieve(
        {
            "required_skills": ["Python", "SQL"],
            "keywords": ["RAG", "LLM"],
            "experience": ["2 years"],
        }
    )

    assert len(results) == 5
    assert all(hasattr(result, "chunk_id") for result in results)
    assert all(hasattr(result, "text") for result in results)


def test_service_retrieve_with_metadata():
    service = KnowledgeBaseService()
    service.index_all()

    result = service.retrieve_with_metadata(
        {
            "required_skills": ["Python"],
            "keywords": ["RAG"],
        }
    )

    assert isinstance(result, dict)
    assert "retrieved_chunks" in result
    assert "count" in result
    assert "indexed_count" in result
    assert "metadata" in result
    assert result["count"] == len(
        result["retrieved_chunks"]
    )
    assert result["indexed_count"] == 17
    assert result["metadata"]["knowledge_base"] is True


def test_service_source_status_reports_all_sources():
    service = KnowledgeBaseService()

    status = service.source_status()

    assert len(status) == 3
    assert all(item["exists"] for item in status)
    assert all(item["is_file"] for item in status)


def test_service_save_and_load(tmp_path):
    service = KnowledgeBaseService()
    service.index_all()

    path = tmp_path / "knowledge_index.json"

    saved = service.save(path)

    assert Path(saved) == path
    assert path.exists()

    restored = KnowledgeBaseService()
    loaded = restored.load(path)

    assert loaded == 17
    assert restored.indexed_count() == 17


def test_service_retrieval_after_load(tmp_path):
    service = KnowledgeBaseService()
    service.index_all()

    path = tmp_path / "knowledge_index.json"
    service.save(path)

    restored = KnowledgeBaseService()
    restored.load(path)

    results = restored.retrieve(
        {
            "required_skills": ["Python", "SQL"],
            "keywords": ["ATS", "RAG"],
        }
    )

    assert len(results) == 5


def test_service_is_indexed_after_indexing():
    service = KnowledgeBaseService()

    assert service.is_indexed() is False

    service.index_all()

    assert service.is_indexed() is True