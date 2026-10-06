"""Persistence utilities for RAG vector indexes."""

import json
from pathlib import Path

from app.rag.models import EmbeddingRecord


class VectorStorePersistence:
    """Save and load vector-store records deterministically."""

    VERSION = 1

    def __init__(self, vector_store, chunk_registry):
        if vector_store is None:
            raise ValueError("vector_store is required.")
        if not hasattr(vector_store, "add"):
            raise TypeError(
                "vector_store must provide an add method."
            )
        if not hasattr(vector_store, "count"):
            raise TypeError(
                "vector_store must provide a count method."
            )

        if chunk_registry is None:
            raise ValueError("chunk_registry is required.")
        if not hasattr(chunk_registry, "add"):
            raise TypeError(
                "chunk_registry must provide an add method."
            )

        self.vector_store = vector_store
        self.chunk_registry = chunk_registry

    def save(self, file_path):
        """Persist the current vector index to disk."""

        if file_path is None:
            raise ValueError("file_path is required.")

        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        records = self._get_records()

        payload = {
            "version": self.VERSION,
            "records": records,
        }

        path.write_text(
            json.dumps(
                payload,
                ensure_ascii=False,
                sort_keys=True,
                indent=2,
            ),
            encoding="utf-8",
        )

        return path

    def load(self, file_path):
        """Load vector records from a persisted index."""

        if file_path is None:
            raise ValueError("file_path is required.")

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Vector index does not exist: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Vector index must be a file: {path}"
            )

        try:
            payload = json.loads(
                path.read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(
                f"Unable to load vector index: {path}"
            ) from exc

        if not isinstance(payload, dict):
            raise ValueError(
                "Vector index payload must be a dictionary."
            )

        if payload.get("version") != self.VERSION:
            raise ValueError(
                "Unsupported vector index version."
            )

        records = payload.get("records")

        if not isinstance(records, list):
            raise ValueError(
                "Vector index records must be a list."
            )

        self._validate_records(records)

        if records:
            embedding_records = [
                EmbeddingRecord.from_dict(record)
                for record in records
            ]

            self.vector_store.add(embedding_records)

        return len(records)

    def _get_records(self):
        """Extract serializable records from the vector store."""

        records = getattr(self.vector_store, "_records", None)

        if records is None:
            raise TypeError(
                "Vector store does not expose persistable records."
            )

        if isinstance(records, dict):
            records = list(records.values())

        if not isinstance(records, list):
            raise TypeError(
                "Vector store records must be a list or dictionary."
            )

        serializable = []

        for record in records:
            if not isinstance(record, EmbeddingRecord):
                raise TypeError(
                    "Each vector store record must be an "
                    "EmbeddingRecord."
                )

            serializable.append(record.to_dict())

        return serializable

    @staticmethod
    def _validate_records(records):
        for record in records:
            if not isinstance(record, dict):
                raise ValueError(
                    "Each persisted record must be a dictionary."
                )

            if "chunk_id" not in record:
                raise ValueError(
                    "Persisted record is missing chunk_id."
                )

            if "vector" not in record:
                raise ValueError(
                    "Persisted record is missing vector."
                )

            if not isinstance(record["vector"], list):
                raise ValueError(
                    "Persisted vector must be a list."
                )