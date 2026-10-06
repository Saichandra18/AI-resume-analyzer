"""Tests for the application-level RAG runtime."""

from pathlib import Path

import app.rag.runtime as runtime


class FakeKnowledgeBaseService:
    """Minimal knowledge-base service for runtime tests."""

    def __init__(self, indexed=False):
        self.indexed = indexed
        self.index_all_calls = 0
        self.save_calls = []
        self.load_calls = []
        self.load_error = None

    def is_indexed(self):
        return self.indexed

    def index_all(self):
        self.index_all_calls += 1
        self.indexed = True

        return [
            {
                "source_id": "test-source",
                "chunk_count": 1,
            }
        ]

    def save(self, file_path):
        self.save_calls.append(Path(file_path))

        path = Path(file_path)
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        path.write_text(
            "persisted",
            encoding="utf-8",
        )

        return path

    def load(self, file_path):
        self.load_calls.append(Path(file_path))

        if self.load_error is not None:
            raise self.load_error

        self.indexed = True

        return 1


def reset_runtime():
    """Reset runtime state between tests."""

    runtime._knowledge_base_service = None


def test_runtime_creates_knowledge_base_once(
    monkeypatch,
    tmp_path,
):
    reset_runtime()

    created = []

    def factory():
        service = FakeKnowledgeBaseService()
        created.append(service)
        return service

    monkeypatch.setattr(
        "app.rag.knowledge.service.KnowledgeBaseService",
        factory,
    )

    index_path = (
        tmp_path / "knowledge_index.json"
    )

    monkeypatch.setattr(
        runtime,
        "_get_index_path",
        lambda: index_path,
    )

    first = runtime.get_knowledge_base_service()
    second = runtime.get_knowledge_base_service()

    assert first is second
    assert len(created) == 1
    assert first.index_all_calls == 1
    assert len(first.save_calls) == 1

def test_runtime_loads_existing_persisted_index(
    monkeypatch,
    tmp_path,
):
    reset_runtime()

    index_path = (
        tmp_path / "knowledge_index.json"
    )
    index_path.write_text(
        "persisted",
        encoding="utf-8",
    )

    service = FakeKnowledgeBaseService()

    monkeypatch.setattr(
        "app.rag.knowledge.service.KnowledgeBaseService",
        lambda: service,
    )

    monkeypatch.setattr(
        runtime,
        "_get_index_path",
        lambda: index_path,
    )

    result = runtime.get_knowledge_base_service()

    assert result is service
    assert service.load_calls == [index_path]
    assert service.index_all_calls == 0
    assert service.save_calls == []


def test_runtime_indexes_and_saves_when_index_missing(
    monkeypatch,
    tmp_path,
):
    reset_runtime()

    index_path = (
        tmp_path / "knowledge_index.json"
    )

    service = FakeKnowledgeBaseService()

    monkeypatch.setattr(
        "app.rag.knowledge.service.KnowledgeBaseService",
        lambda: service,
    )

    monkeypatch.setattr(
        runtime,
        "_get_index_path",
        lambda: index_path,
    )

    result = runtime.get_knowledge_base_service()

    assert result is service
    assert service.load_calls == []
    assert service.index_all_calls == 1
    assert service.save_calls == [index_path]
    assert index_path.exists()


def test_runtime_rebuilds_corrupt_persisted_index(
    monkeypatch,
    tmp_path,
):
    reset_runtime()

    index_path = (
        tmp_path / "knowledge_index.json"
    )
    index_path.write_text(
        "corrupt",
        encoding="utf-8",
    )

    service = FakeKnowledgeBaseService(
        indexed=False
    )
    service.load_error = ValueError(
        "Unsupported vector index version."
    )

    monkeypatch.setattr(
        "app.rag.knowledge.service.KnowledgeBaseService",
        lambda: service,
    )

    monkeypatch.setattr(
        runtime,
        "_get_index_path",
        lambda: index_path,
    )

    result = runtime.get_knowledge_base_service()

    assert result is service
    assert service.load_calls == [index_path]
    assert service.index_all_calls == 1
    assert service.save_calls == [index_path]


def test_runtime_does_not_rebuild_already_indexed_service(
    monkeypatch,
    tmp_path,
):
    reset_runtime()

    index_path = (
        tmp_path / "knowledge_index.json"
    )

    service = FakeKnowledgeBaseService(
        indexed=True
    )

    monkeypatch.setattr(
        "app.rag.knowledge.service.KnowledgeBaseService",
        lambda: service,
    )

    monkeypatch.setattr(
        runtime,
        "_get_index_path",
        lambda: index_path,
    )

    result = runtime.get_knowledge_base_service()

    assert result is service
    assert service.load_calls == []
    assert service.index_all_calls == 0
    assert service.save_calls == []


def test_runtime_reuses_same_service_after_initialization(
    monkeypatch,
    tmp_path,
):
    reset_runtime()

    index_path = (
        tmp_path / "knowledge_index.json"
    )

    created = []

    def factory():
        service = FakeKnowledgeBaseService()
        created.append(service)
        return service

    monkeypatch.setattr(
        "app.rag.knowledge.service.KnowledgeBaseService",
        factory,
    )

    monkeypatch.setattr(
        runtime,
        "_get_index_path",
        lambda: index_path,
    )

    first = runtime.get_knowledge_base_service()
    second = runtime.get_knowledge_base_service()
    third = runtime.get_knowledge_base_service()

    assert first is second
    assert second is third
    assert len(created) == 1
    assert first.index_all_calls == 1
    assert len(first.save_calls) == 1

def test_runtime_uses_configured_index_path(
    monkeypatch,
    tmp_path,
):
    reset_runtime()

    configured_path = (
        tmp_path
        / "custom"
        / "rag"
        / "knowledge_index.json"
    )

    service = FakeKnowledgeBaseService()

    monkeypatch.setenv(
        "RAG_KNOWLEDGE_INDEX_PATH",
        str(configured_path),
    )

    monkeypatch.setattr(
        "app.rag.knowledge.service.KnowledgeBaseService",
        lambda: service,
    )

    result = runtime.get_knowledge_base_service()

    assert result is service
    assert service.index_all_calls == 1
    assert service.save_calls == [
        configured_path
    ]
    assert configured_path.exists()