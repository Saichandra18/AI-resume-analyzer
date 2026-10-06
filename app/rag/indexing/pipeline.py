"""End-to-end knowledge ingestion and indexing pipeline."""

from pathlib import Path

from app.rag.ingestion.pipeline import IngestionPipeline


class KnowledgeIndexingPipeline:
    """Ingest source documents and index their chunks into the RAG store."""

    def __init__(
        self,
        ingestion_pipeline=None,
        indexer=None,
    ):
        if ingestion_pipeline is not None and not hasattr(
            ingestion_pipeline,
            "ingest",
        ):
            raise TypeError(
                "ingestion_pipeline must provide an ingest method."
            )

        if indexer is not None and not hasattr(indexer, "index"):
            raise TypeError(
                "indexer must provide an index method."
            )

        self.ingestion_pipeline = (
            ingestion_pipeline
            if ingestion_pipeline is not None
            else IngestionPipeline()
        )
        self.indexer = indexer

    def index_file(
        self,
        file_path,
        document_id=None,
        metadata=None,
    ):
        """Ingest and index a single source file."""

        if file_path is None:
            raise ValueError("file_path is required.")

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Knowledge source does not exist: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Knowledge source must be a file: {path}"
            )

        if self.indexer is None:
            raise RuntimeError(
                "A knowledge indexer is required for indexing."
            )

        chunks = self.ingestion_pipeline.ingest(
            path,
            document_id=document_id,
            metadata=metadata,
        )

        indexed_chunk_ids = self.indexer.index(chunks)

        return {
            "file_path": str(path),
            "document_id": document_id or path.stem,
            "chunk_count": len(chunks),
            "indexed_chunk_ids": list(indexed_chunk_ids),
        }

    def index_chunks(self, chunks):
        """Index already-ingested document chunks."""

        if self.indexer is None:
            raise RuntimeError(
                "A knowledge indexer is required for indexing."
            )

        return self.indexer.index(chunks)