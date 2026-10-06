import json

import pytest

from app.rag.models import DocumentChunk, EmbeddingRecord
from app.rag.vectorstore.in_memory import InMemoryVectorStore
from app.rag.vectorstore.persistence import VectorStorePersistence
from app.rag.vectorstore.registry import ChunkRegistry


def make_chunk(chunk_id="chunk-1", text="Python developer"):
    return DocumentChunk(
        chunk_id=chunk_id,
        document_id="doc-1",
        text=text,
        metadata={"source": "knowledge"},
    )


def make_store_with_record():
    store = InMemoryVectorStore()

    store.add(
        [
            EmbeddingRecord(
                chunk_id="chunk-1",
                vector=[1.0, 0.0, 0.0],
                model="test-model",
                dimensions=3,
                metadata={"source": "knowledge"},
            )
        ]
    )

    return store
def test_persistence_requires_dependencies():
    with pytest.raises(ValueError):
        VectorStorePersistence(
            None,
            ChunkRegistry(),
        )

    with pytest.raises(ValueError):
        VectorStorePersistence(
            InMemoryVectorStore(),
            None,
        )


def test_persistence_rejects_invalid_dependencies():
    with pytest.raises(TypeError):
        VectorStorePersistence(
            object(),
            ChunkRegistry(),
        )

    with pytest.raises(TypeError):
        VectorStorePersistence(
            InMemoryVectorStore(),
            object(),
        )


def test_save_requires_file_path():
    persistence = VectorStorePersistence(
        InMemoryVectorStore(),
        ChunkRegistry(),
    )

    with pytest.raises(ValueError):
        persistence.save(None)


def test_save_and_load_round_trip(tmp_path):
    source_store = make_store_with_record()
    source_registry = ChunkRegistry()
    source_registry.add([make_chunk()])

    persistence = VectorStorePersistence(
        source_store,
        source_registry,
    )

    path = tmp_path / "index.json"

    saved_path = persistence.save(path)

    assert saved_path == path
    assert path.exists()

    target_store = InMemoryVectorStore()
    target_registry = ChunkRegistry()

    loaded = VectorStorePersistence(
        target_store,
        target_registry,
    )

    count = loaded.load(path)

    assert count == 1
    assert target_store.count() == 1


def test_save_creates_parent_directories(tmp_path):
    store = make_store_with_record()
    registry = ChunkRegistry()

    persistence = VectorStorePersistence(
        store,
        registry,
    )

    path = tmp_path / "nested" / "rag" / "index.json"

    persistence.save(path)

    assert path.exists()


def test_empty_index_can_be_saved_and_loaded(tmp_path):
    source = VectorStorePersistence(
        InMemoryVectorStore(),
        ChunkRegistry(),
    )

    path = tmp_path / "empty.json"

    source.save(path)

    target_store = InMemoryVectorStore()
    target_registry = ChunkRegistry()

    target = VectorStorePersistence(
        target_store,
        target_registry,
    )

    assert target.load(path) == 0
    assert target_store.count() == 0


def test_load_requires_existing_file(tmp_path):
    persistence = VectorStorePersistence(
        InMemoryVectorStore(),
        ChunkRegistry(),
    )

    with pytest.raises(FileNotFoundError):
        persistence.load(tmp_path / "missing.json")


def test_load_rejects_directory(tmp_path):
    directory = tmp_path / "index"
    directory.mkdir()

    persistence = VectorStorePersistence(
        InMemoryVectorStore(),
        ChunkRegistry(),
    )

    with pytest.raises(ValueError):
        persistence.load(directory)


def test_load_rejects_invalid_json(tmp_path):
    path = tmp_path / "invalid.json"
    path.write_text("{invalid", encoding="utf-8")

    persistence = VectorStorePersistence(
        InMemoryVectorStore(),
        ChunkRegistry(),
    )

    with pytest.raises(ValueError):
        persistence.load(path)


def test_load_rejects_wrong_version(tmp_path):
    path = tmp_path / "index.json"

    path.write_text(
        json.dumps(
            {
                "version": 999,
                "records": [],
            }
        ),
        encoding="utf-8",
    )

    persistence = VectorStorePersistence(
        InMemoryVectorStore(),
        ChunkRegistry(),
    )

    with pytest.raises(ValueError):
        persistence.load(path)


def test_load_rejects_invalid_records(tmp_path):
    path = tmp_path / "index.json"

    path.write_text(
        json.dumps(
            {
                "version": 1,
                "records": [
                    {
                        "chunk_id": "chunk-1",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    persistence = VectorStorePersistence(
        InMemoryVectorStore(),
        ChunkRegistry(),
    )

    with pytest.raises(ValueError):
        persistence.load(path)


def test_save_produces_versioned_json(tmp_path):
    persistence = VectorStorePersistence(
        make_store_with_record(),
        ChunkRegistry(),
    )

    path = tmp_path / "index.json"

    persistence.save(path)

    payload = json.loads(
        path.read_text(encoding="utf-8")
    )

    assert payload["version"] == 1
    assert len(payload["records"]) == 1
    assert payload["records"][0]["chunk_id"] == "chunk-1"