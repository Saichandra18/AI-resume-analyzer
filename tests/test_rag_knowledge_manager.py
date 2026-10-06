import pytest

from app.rag.knowledge.manager import KnowledgeBaseManager
from app.rag.knowledge.sources import (
    KnowledgeSource,
    KnowledgeSourceCatalog,
)


class FakeIndexingPipeline:
    def __init__(self):
        self.calls = []
        self.indexer = FakeIndexerContainer()

    def index_file(
        self,
        file_path,
        document_id=None,
        metadata=None,
    ):
        self.calls.append(
            {
                "file_path": file_path,
                "document_id": document_id,
                "metadata": metadata,
            }
        )

        return {
            "file_path": str(file_path),
            "document_id": document_id,
            "chunk_count": 2,
            "indexed_chunk_ids": [
                f"{document_id}:0",
                f"{document_id}:1",
            ],
        }


class FakeVectorStore:
    def __init__(self):
        self.total = 0

    def count(self):
        return self.total


class FakeIndexerContainer:
    def __init__(self):
        self.vector_store = FakeVectorStore()


class FakePersistence:
    def __init__(self):
        self.save_calls = []
        self.load_calls = []

    def save(self, file_path):
        self.save_calls.append(file_path)
        return file_path

    def load(self, file_path):
        self.load_calls.append(file_path)
        return 3


def make_source(
    source_id="ats-guidelines",
    file_path=None,
    category="ats",
):
    return KnowledgeSource(
        source_id=source_id,
        file_path=str(file_path or "ats.txt"),
        category=category,
        description="Test knowledge source",
        metadata={
            "source_type": "built_in",
            "filename": "ats.txt",
        },
    )


def make_catalog(tmp_path):
    source = make_source(
        file_path=tmp_path / "ats.txt",
    )
    catalog = KnowledgeSourceCatalog([source])
    return catalog, source


def test_manager_requires_catalog():
    with pytest.raises(ValueError):
        KnowledgeBaseManager(
            None,
            FakeIndexingPipeline(),
        )


def test_manager_rejects_invalid_catalog():
    with pytest.raises(TypeError):
        KnowledgeBaseManager(
            object(),
            FakeIndexingPipeline(),
        )


def test_manager_requires_indexing_pipeline():
    catalog = KnowledgeSourceCatalog()

    with pytest.raises(ValueError):
        KnowledgeBaseManager(
            catalog,
            None,
        )


def test_manager_rejects_invalid_indexing_pipeline():
    catalog = KnowledgeSourceCatalog()

    with pytest.raises(TypeError):
        KnowledgeBaseManager(
            catalog,
            object(),
        )


def test_manager_accepts_optional_persistence():
    catalog = KnowledgeSourceCatalog()
    persistence = FakePersistence()

    manager = KnowledgeBaseManager(
        catalog,
        FakeIndexingPipeline(),
        persistence,
    )

    assert manager.persistence is persistence


def test_manager_rejects_invalid_persistence():
    catalog = KnowledgeSourceCatalog()

    with pytest.raises(TypeError):
        KnowledgeBaseManager(
            catalog,
            FakeIndexingPipeline(),
            object(),
        )


def test_index_source_requires_string_id(tmp_path):
    catalog, _ = make_catalog(tmp_path)

    manager = KnowledgeBaseManager(
        catalog,
        FakeIndexingPipeline(),
    )

    with pytest.raises(TypeError):
        manager.index_source(None)


def test_index_source_rejects_unknown_source(tmp_path):
    catalog, _ = make_catalog(tmp_path)

    manager = KnowledgeBaseManager(
        catalog,
        FakeIndexingPipeline(),
    )

    with pytest.raises(KeyError):
        manager.index_source("missing")


def test_index_source_requires_existing_file(tmp_path):
    catalog, source = make_catalog(tmp_path)

    manager = KnowledgeBaseManager(
        catalog,
        FakeIndexingPipeline(),
    )

    with pytest.raises(FileNotFoundError):
        manager.index_source(source.source_id)


def test_index_source_rejects_directory(tmp_path):
    directory = tmp_path / "ats"
    directory.mkdir()

    catalog = KnowledgeSourceCatalog(
        [
            make_source(
                file_path=directory,
            )
        ]
    )

    manager = KnowledgeBaseManager(
        catalog,
        FakeIndexingPipeline(),
    )

    with pytest.raises(ValueError):
        manager.index_source("ats-guidelines")


def test_index_source_calls_indexing_pipeline(tmp_path):
    source_file = tmp_path / "ats.txt"
    source_file.write_text("ATS guidance")

    catalog = KnowledgeSourceCatalog(
        [
            make_source(
                file_path=source_file,
            )
        ]
    )

    indexing = FakeIndexingPipeline()

    manager = KnowledgeBaseManager(
        catalog,
        indexing,
    )

    result = manager.index_source("ats-guidelines")

    assert result["source_id"] == "ats-guidelines"
    assert result["category"] == "ats"
    assert result["document_id"] == "ats-guidelines"
    assert result["chunk_count"] == 2
    assert result["indexed_chunk_ids"] == [
        "ats-guidelines:0",
        "ats-guidelines:1",
    ]

    assert len(indexing.calls) == 1
    assert indexing.calls[0]["file_path"] == source_file
    assert indexing.calls[0]["document_id"] == "ats-guidelines"


def test_index_source_adds_source_metadata(tmp_path):
    source_file = tmp_path / "ats.txt"
    source_file.write_text("ATS guidance")

    catalog = KnowledgeSourceCatalog(
        [
            make_source(
                file_path=source_file,
            )
        ]
    )

    indexing = FakeIndexingPipeline()

    manager = KnowledgeBaseManager(
        catalog,
        indexing,
    )

    manager.index_source("ats-guidelines")

    metadata = indexing.calls[0]["metadata"]

    assert metadata["source_type"] == "built_in"
    assert metadata["filename"] == "ats.txt"
    assert metadata["source_id"] == "ats-guidelines"
    assert metadata["source_category"] == "ats"


def test_index_source_does_not_modify_source_metadata(tmp_path):
    source_file = tmp_path / "ats.txt"
    source_file.write_text("ATS guidance")

    source = make_source(
        file_path=source_file,
    )

    catalog = KnowledgeSourceCatalog([source])
    indexing = FakeIndexingPipeline()

    manager = KnowledgeBaseManager(
        catalog,
        indexing,
    )

    manager.index_source(source.source_id)

    assert source.metadata == {
        "source_type": "built_in",
        "filename": "ats.txt",
    }


def test_index_all_indexes_every_source(tmp_path):
    files = []

    sources = []

    for source_id in (
        "source-a",
        "source-b",
        "source-c",
    ):
        path = tmp_path / f"{source_id}.txt"
        path.write_text(source_id)
        files.append(path)

        sources.append(
            make_source(
                source_id=source_id,
                file_path=path,
            )
        )

    catalog = KnowledgeSourceCatalog(sources)
    indexing = FakeIndexingPipeline()

    manager = KnowledgeBaseManager(
        catalog,
        indexing,
    )

    result = manager.index_all()

    assert len(result) == 3
    assert [
        item["source_id"]
        for item in result
    ] == [
        "source-a",
        "source-b",
        "source-c",
    ]

    assert len(indexing.calls) == 3


def test_source_status_reports_existing_files(tmp_path):
    source_file = tmp_path / "ats.txt"
    source_file.write_text("ATS")

    catalog = KnowledgeSourceCatalog(
        [
            make_source(
                file_path=source_file,
            )
        ]
    )

    manager = KnowledgeBaseManager(
        catalog,
        FakeIndexingPipeline(),
    )

    status = manager.source_status()

    assert status == [
        {
            "source_id": "ats-guidelines",
            "category": "ats",
            "file_path": str(source_file),
            "exists": True,
            "is_file": True,
        }
    ]


def test_source_status_reports_missing_files(tmp_path):
    missing = tmp_path / "missing.txt"

    catalog = KnowledgeSourceCatalog(
        [
            make_source(
                file_path=missing,
            )
        ]
    )

    manager = KnowledgeBaseManager(
        catalog,
        FakeIndexingPipeline(),
    )

    status = manager.source_status()

    assert status[0]["exists"] is False
    assert status[0]["is_file"] is False


def test_save_requires_persistence():
    manager = KnowledgeBaseManager(
        KnowledgeSourceCatalog(),
        FakeIndexingPipeline(),
    )

    with pytest.raises(RuntimeError):
        manager.save("index.json")


def test_load_requires_persistence():
    manager = KnowledgeBaseManager(
        KnowledgeSourceCatalog(),
        FakeIndexingPipeline(),
    )

    with pytest.raises(RuntimeError):
        manager.load("index.json")


def test_save_delegates_to_persistence(tmp_path):
    persistence = FakePersistence()

    manager = KnowledgeBaseManager(
        KnowledgeSourceCatalog(),
        FakeIndexingPipeline(),
        persistence,
    )

    index_file = tmp_path / "index.json"

    result = manager.save(index_file)

    assert result == index_file
    assert persistence.save_calls == [index_file]


def test_load_delegates_to_persistence(tmp_path):
    persistence = FakePersistence()

    manager = KnowledgeBaseManager(
        KnowledgeSourceCatalog(),
        FakeIndexingPipeline(),
        persistence,
    )

    index_file = tmp_path / "index.json"

    result = manager.load(index_file)

    assert result == 3
    assert persistence.load_calls == [index_file]


def test_indexed_count_uses_vector_store():
    indexing = FakeIndexingPipeline()
    indexing.indexer.vector_store.total = 7

    manager = KnowledgeBaseManager(
        KnowledgeSourceCatalog(),
        indexing,
    )

    assert manager.indexed_count() == 7


def test_indexed_count_rejects_pipeline_without_vector_store():
    class PipelineWithoutVectorStore:
        indexer = None

        def index_file(self, *args, **kwargs):
            return {}

    manager = KnowledgeBaseManager(
        KnowledgeSourceCatalog(),
        PipelineWithoutVectorStore(),
    )

    with pytest.raises(TypeError):
        manager.indexed_count()


def test_index_source_preserves_custom_metadata(tmp_path):
    source_file = tmp_path / "guide.txt"
    source_file.write_text("Guide")

    source = KnowledgeSource(
        source_id="guide",
        file_path=str(source_file),
        category="custom",
        description="Custom guide",
        metadata={
            "source_type": "custom",
            "owner": "project",
        },
    )

    catalog = KnowledgeSourceCatalog([source])
    indexing = FakeIndexingPipeline()

    manager = KnowledgeBaseManager(
        catalog,
        indexing,
    )

    manager.index_source("guide")

    metadata = indexing.calls[0]["metadata"]

    assert metadata["source_type"] == "custom"
    assert metadata["owner"] == "project"
    assert metadata["source_id"] == "guide"
    assert metadata["source_category"] == "custom"


def test_index_all_returns_empty_for_empty_catalog():
    indexing = FakeIndexingPipeline()

    manager = KnowledgeBaseManager(
        KnowledgeSourceCatalog(),
        indexing,
    )

    assert manager.index_all() == []
    assert indexing.calls == []


def test_indexed_count_returns_zero_for_empty_vector_store():
    manager = KnowledgeBaseManager(
        KnowledgeSourceCatalog(),
        FakeIndexingPipeline(),
    )

    assert manager.indexed_count() == 0