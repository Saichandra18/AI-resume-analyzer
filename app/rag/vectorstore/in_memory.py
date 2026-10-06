
"""In-memory vector store for RAG retrieval."""

import math

from app.rag.interfaces import VectorStore
from app.rag.models import EmbeddingRecord, RetrievedChunk


class InMemoryVectorStore(VectorStore):
    """Store embeddings in memory and perform similarity search."""

    def __init__(self, chunk_registry=None):
        self._records = {}
        self.chunk_registry = chunk_registry

    def add(self, records):
        """Add embedding records to the store."""

        if not isinstance(records, (list, tuple)):
            raise TypeError(
                "records must be a list or tuple."
            )

        for record in records:
            record = self._normalize_record(record)

            self._validate_vector(record.vector)

            self._records[record.chunk_id] = record

    @staticmethod
    def _normalize_record(record):
        """Normalize supported record representations."""

        if isinstance(record, EmbeddingRecord):
            return record

        if isinstance(record, dict):
            if "chunk_id" not in record:
                raise ValueError(
                    "Embedding record must contain chunk_id."
                )

            if "embedding" not in record:
                raise ValueError(
                    "Embedding record must contain embedding."
                )

            embedding = record["embedding"]

            return EmbeddingRecord(
                chunk_id=record["chunk_id"],
                vector=embedding,
                model=record.get("model", ""),
                dimensions=record.get(
                    "dimensions",
                    len(embedding),
                ),
                metadata=dict(
                    record.get("metadata", {})
                ),
            )

        raise TypeError(
            "records must contain "
            "EmbeddingRecord or dictionary objects."
        )

    def _build_retrieved_chunk(self, record, score):
        """Build a RetrievedChunk using the original DocumentChunk when available."""

        chunk = None

        if self.chunk_registry is not None:
            chunk = self.chunk_registry.get(record.chunk_id)

        if chunk is not None:
            return RetrievedChunk(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                text=chunk.text,
                score=score,
                metadata=dict(chunk.metadata),
            )

        return RetrievedChunk(
            chunk_id=record.chunk_id,
            document_id=record.chunk_id.rsplit(
                ":",
                1,
            )[0],
            text=record.metadata.get(
                "text",
                "",
            ),
            score=score,
            metadata=dict(record.metadata),
        )

    def search(
        self,
        query_vector,
        top_k=5,
        filters=None,
    ):
        """Return the most similar stored chunks."""

        self._validate_vector(query_vector)

        if not isinstance(top_k, int):
            raise TypeError(
                "top_k must be an integer."
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be positive."
            )

        if filters is not None and not isinstance(
            filters,
            dict,
        ):
            raise TypeError(
                "filters must be a dictionary."
            )

        scored = []

        for record in self._records.values():
            if not self._matches_filters(
                record,
                filters,
            ):
                continue

            similarity = self._cosine_similarity(
                query_vector,
                record.vector,
            )

            scored.append(
                (similarity, record)
            )

        scored.sort(
            key=lambda item: (
                -item[0],
                item[1].chunk_id,
            )
        )

        return [
            self._build_retrieved_chunk(
                record,
                score,
            )
            for score, record in scored[:top_k]
        ]

    def delete(self, chunk_ids):
        """Delete records by chunk ID."""

        if not isinstance(
            chunk_ids,
            (list, tuple),
        ):
            raise TypeError(
                "chunk_ids must be a list or tuple."
            )

        for chunk_id in chunk_ids:
            self._records.pop(
                chunk_id,
                None,
            )

    def count(self):
        """Return the number of stored records."""

        return len(self._records)

    @staticmethod
    def _validate_vector(vector):
        """Validate a vector."""

        if not isinstance(
            vector,
            (list, tuple),
        ):
            raise TypeError(
                "Vector must be a list or tuple."
            )

        if not vector:
            raise ValueError(
                "Vector cannot be empty."
            )

        if any(
            not isinstance(value, (int, float))
            for value in vector
        ):
            raise TypeError(
                "Vector values must be numeric."
            )

        if any(
            not math.isfinite(value)
            for value in vector
        ):
            raise ValueError(
                "Vector values must be finite."
            )

    @staticmethod
    def _cosine_similarity(
        first,
        second,
    ):
        """Calculate cosine similarity."""

        if len(first) != len(second):
            raise ValueError(
                "Vectors must have the same dimension."
            )

        first_magnitude = math.sqrt(
            sum(value * value for value in first)
        )

        second_magnitude = math.sqrt(
            sum(value * value for value in second)
        )

        if (
            first_magnitude == 0
            or second_magnitude == 0
        ):
            return 0.0

        dot_product = sum(
            left * right
            for left, right in zip(
                first,
                second,
            )
        )

        return (
            dot_product
            / (
                first_magnitude
                * second_magnitude
            )
        )

    @staticmethod
    def _matches_filters(
        record,
        filters,
    ):
        """Check metadata filters."""

        if not filters:
            return True

        metadata = record.metadata

        return all(
            metadata.get(key) == value
            for key, value in filters.items()
        )
