import pytest

from app.rag.indexing import KnowledgeIndexingPipeline


class FakeIngestionPipeline:
    def __init__(self):
        self.calls = []

    def ingest(self, file_path, document_id=None, metadata=None):
        self.calls.append(
            {
                "file_path": file_path,
                "document_id": document_id,
                "metadata": metadata,
            }
        )

        return [
            type(
                "Chunk",
                (),
                {"chunk_id": "chunk-1"},
            )(),
            type(
                "Chunk",
                (),
                {"chunk_id": "chunk-2"},
            )(),
        ]


class FakeIndexer:
    def __init__(self):
        self.calls = []

    def index(self, chunks):
        self.calls.append(chunks)
        return [chunk.chunk_id for chunk in chunks]


def test_pipeline_requires_valid_ingestion_pipeline():
    with pytest.raises(TypeError):
        KnowledgeIndexingPipeline(
            ingestion_pipeline=object(),
            indexer=FakeIndexer(),
        )


def test_pipeline_requires_valid_indexer():
    with pytest.raises(TypeError):
        KnowledgeIndexingPipeline(
            ingestion_pipeline=FakeIngestionPipeline(),
            indexer=object(),
        )


def test_index_file_requires_file_path():
    pipeline = KnowledgeIndexingPipeline(
        ingestion_pipeline=FakeIngestionPipeline(),
        indexer=FakeIndexer(),
    )

    with pytest.raises(ValueError):
        pipeline.index_file(None)


def test_index_file_requires_existing_file(tmp_path):
    pipeline = KnowledgeIndexingPipeline(
        ingestion_pipeline=FakeIngestionPipeline(),
        indexer=FakeIndexer(),
    )

    missing_file = tmp_path / "missing.txt"

    with pytest.raises(FileNotFoundError):
        pipeline.index_file(missing_file)


def test_index_file_rejects_directory(tmp_path):
    pipeline = KnowledgeIndexingPipeline(
        ingestion_pipeline=FakeIngestionPipeline(),
        indexer=FakeIndexer(),
    )

    directory = tmp_path / "knowledge"
    directory.mkdir()

    with pytest.raises(ValueError):
        pipeline.index_file(directory)


def test_index_file_requires_indexer(tmp_path):
    source = tmp_path / "knowledge.txt"
    source.write_text("Python developer")

    pipeline = KnowledgeIndexingPipeline(
        ingestion_pipeline=FakeIngestionPipeline(),
        indexer=None,
    )

    with pytest.raises(RuntimeError):
        pipeline.index_file(source)


def test_index_file_runs_ingestion_then_indexing(tmp_path):
    source = tmp_path / "knowledge.txt"
    source.write_text("Python developer")

    ingestion = FakeIngestionPipeline()
    indexer = FakeIndexer()

    pipeline = KnowledgeIndexingPipeline(
        ingestion_pipeline=ingestion,
        indexer=indexer,
    )

    result = pipeline.index_file(source)

    assert result["file_path"] == str(source)
    assert result["document_id"] == "knowledge"
    assert result["chunk_count"] == 2
    assert result["indexed_chunk_ids"] == [
        "chunk-1",
        "chunk-2",
    ]

    assert len(ingestion.calls) == 1
    assert ingestion.calls[0]["file_path"] == source

    assert len(indexer.calls) == 1
    assert len(indexer.calls[0]) == 2


def test_index_file_passes_document_id_and_metadata(tmp_path):
    source = tmp_path / "knowledge.txt"
    source.write_text("Python developer")

    ingestion = FakeIngestionPipeline()
    indexer = FakeIndexer()

    pipeline = KnowledgeIndexingPipeline(
        ingestion_pipeline=ingestion,
        indexer=indexer,
    )

    metadata = {
        "source": "approved-knowledge",
        "category": "technical",
    }

    result = pipeline.index_file(
        source,
        document_id="python-doc",
        metadata=metadata,
    )

    assert result["document_id"] == "python-doc"

    assert ingestion.calls[0]["document_id"] == "python-doc"
    assert ingestion.calls[0]["metadata"] == metadata


def test_index_chunks_delegates_to_indexer():
    indexer = FakeIndexer()

    pipeline = KnowledgeIndexingPipeline(
        ingestion_pipeline=FakeIngestionPipeline(),
        indexer=indexer,
    )

    chunks = [
        type("Chunk", (), {"chunk_id": "chunk-1"})(),
    ]

    result = pipeline.index_chunks(chunks)

    assert result == ["chunk-1"]
    assert indexer.calls == [chunks]


def test_index_chunks_requires_indexer():
    pipeline = KnowledgeIndexingPipeline(
        ingestion_pipeline=FakeIngestionPipeline(),
        indexer=None,
    )

    with pytest.raises(RuntimeError):
        pipeline.index_chunks([])