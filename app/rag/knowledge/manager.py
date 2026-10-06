"""Knowledge-base management and indexing orchestration."""

from copy import deepcopy
from pathlib import Path


class KnowledgeBaseManager:
    """Manage approved knowledge sources and their indexed content."""

    def __init__(
        self,
        catalog,
        indexing_pipeline,
        persistence=None,
    ):
        if catalog is None:
            raise ValueError("catalog is required.")

        if not hasattr(catalog, "list_sources"):
            raise TypeError(
                "catalog must provide a list_sources method."
            )

        if indexing_pipeline is None:
            raise ValueError(
                "indexing_pipeline is required."
            )

        if not hasattr(indexing_pipeline, "index_file"):
            raise TypeError(
                "indexing_pipeline must provide an index_file method."
            )

        if persistence is not None and not hasattr(
            persistence,
            "save",
        ):
            raise TypeError(
                "persistence must provide a save method."
            )

        if persistence is not None and not hasattr(
            persistence,
            "load",
        ):
            raise TypeError(
                "persistence must provide a load method."
            )

        self.catalog = catalog
        self.indexing_pipeline = indexing_pipeline
        self.persistence = persistence

    def index_source(self, source_id):
        """Index one approved knowledge source."""

        source = self._get_source(source_id)

        path = Path(source.file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Knowledge source does not exist: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Knowledge source must be a file: {path}"
            )

        metadata = deepcopy(source.metadata)

        metadata.update(
            {
                "source_id": source.source_id,
                "source_category": source.category,
                "source_type": metadata.get(
                    "source_type",
                    "knowledge",
                ),
            }
        )

        result = self.indexing_pipeline.index_file(
            path,
            document_id=source.source_id,
            metadata=metadata,
        )

        return {
            "source_id": source.source_id,
            "category": source.category,
            "file_path": str(path),
            "document_id": result["document_id"],
            "chunk_count": result["chunk_count"],
            "indexed_chunk_ids": list(
                result["indexed_chunk_ids"]
            ),
        }

    def index_all(self):
        """Index every approved knowledge source."""

        results = []

        for source in self.catalog.list_sources():
            results.append(
                self.index_source(source.source_id)
            )

        return results

    def source_status(self):
        """Return deterministic status information for all sources."""

        status = []

        for source in self.catalog.list_sources():
            path = Path(source.file_path)

            status.append(
                {
                    "source_id": source.source_id,
                    "category": source.category,
                    "file_path": str(path),
                    "exists": path.exists(),
                    "is_file": path.is_file(),
                }
            )

        return status

    def save(self, file_path):
        """Persist the current knowledge-base vector index."""

        if self.persistence is None:
            raise RuntimeError(
                "Persistence is required for saving."
            )

        return self.persistence.save(file_path)

    def load(self, file_path):
        """Load a persisted knowledge-base vector index."""

        if self.persistence is None:
            raise RuntimeError(
                "Persistence is required for loading."
            )

        return self.persistence.load(file_path)

    def indexed_count(self):
        """Return the number of indexed vector records."""

        vector_store = getattr(
            self.indexing_pipeline,
            "indexer",
            None,
        )

        vector_store = getattr(
            vector_store,
            "vector_store",
            None,
        )

        if vector_store is None or not hasattr(
            vector_store,
            "count",
        ):
            raise TypeError(
                "Indexing pipeline does not expose a countable "
                "vector store."
            )

        return vector_store.count()

    def _get_source(self, source_id):
        if not isinstance(source_id, str):
            raise TypeError(
                "source_id must be a string."
            )

        source = self.catalog.get(source_id)

        if source is None:
            raise KeyError(
                f"Unknown knowledge source: {source_id}"
            )

        return source