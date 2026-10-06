"""Tests for the RAG ingestion pipeline."""

from pathlib import Path

import pytest

from app.rag.ingestion.chunker import DocumentChunker
from app.rag.ingestion.pipeline import IngestionPipeline


def test_ingest_text_file(tmp_path):
    file_path = tmp_path / "python.txt"

    file_path.write_text(
        "Python is a programming language.\n\n"
        "Flask is a web framework.",
        encoding="utf-8",
    )

    pipeline = IngestionPipeline()

    chunks = pipeline.ingest(file_path)

    assert len(chunks) == 1
    assert chunks[0].document_id == "python"
    assert "Python" in chunks[0].text
    assert "Flask" in chunks[0].text


def test_ingest_uses_explicit_document_id(tmp_path):
    file_path = tmp_path / "knowledge.txt"

    file_path.write_text(
        "Python is useful.",
        encoding="utf-8",
    )

    pipeline = IngestionPipeline()

    chunks = pipeline.ingest(
        file_path,
        document_id="python-guide",
    )

    assert chunks[0].document_id == "python-guide"
    assert chunks[0].chunk_id == "python-guide:0"


def test_ingest_passes_metadata_to_chunks(tmp_path):
    file_path = tmp_path / "knowledge.txt"

    file_path.write_text(
        "Python is useful.",
        encoding="utf-8",
    )

    metadata = {
        "source": "official-docs",
        "category": "python",
    }

    pipeline = IngestionPipeline()

    chunks = pipeline.ingest(
        file_path,
        document_id="python-doc",
        metadata=metadata,
    )

    assert chunks[0].metadata["source"] == "official-docs"
    assert chunks[0].metadata["category"] == "python"
    assert chunks[0].metadata["document_id"] == "python-doc"


def test_ingest_applies_parser_and_cleaner(tmp_path):
    file_path = tmp_path / "knowledge.txt"

    file_path.write_text(
        "   Python     Flask   \n\n\n"
        "   RAG     retrieval   ",
        encoding="utf-8",
    )

    pipeline = IngestionPipeline()

    chunks = pipeline.ingest(file_path)

    assert chunks[0].text == (
        "Python Flask\nRAG retrieval"
    )


def test_ingest_supports_custom_chunker(tmp_path):
    file_path = tmp_path / "knowledge.txt"

    file_path.write_text(
        "Python is a programming language.\n"
        "Flask is a web framework.\n"
        "RAG provides contextual retrieval.",
        encoding="utf-8",
    )

    chunker = DocumentChunker(
        chunk_size=40,
        overlap=5,
    )

    pipeline = IngestionPipeline(
        chunker=chunker,
    )

    chunks = pipeline.ingest(
        file_path,
        document_id="tech",
    )

    assert len(chunks) >= 2
    assert chunks[0].chunk_id == "tech:0"


def test_ingest_missing_file_propagates_error(tmp_path):
    pipeline = IngestionPipeline()

    with pytest.raises(FileNotFoundError):
        pipeline.ingest(
            tmp_path / "missing.txt"
        )