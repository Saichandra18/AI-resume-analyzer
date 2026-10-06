"""Embedding generation and validation for RAG document chunks."""

from app.rag.models import DocumentChunk, EmbeddingRecord


class EmbeddingGenerator:
    """Generate and validate embedding records from document chunks."""

    def __init__(self, provider):
        if provider is None:
            raise ValueError(
                "provider cannot be None."
            )

        if not hasattr(provider, "generate_embedding"):
            raise TypeError(
                "provider must implement "
                "generate_embedding."
            )

        self.provider = provider

    def generate(self, chunk):
        """Generate and validate an EmbeddingRecord."""

        if not isinstance(chunk, DocumentChunk):
            raise TypeError(
                "chunk must be a DocumentChunk."
            )

        vector = self.provider.generate_embedding(
            chunk.text
        )

        self._validate_vector(vector)

        return EmbeddingRecord(
            chunk_id=chunk.chunk_id,
            vector=vector,
        )

    def generate_batch(self, chunks):
        """Generate embedding records for multiple chunks."""

        if not isinstance(chunks, (list, tuple)):
            raise TypeError(
                "chunks must be a list or tuple."
            )

        return [
            self.generate(chunk)
            for chunk in chunks
        ]

    @staticmethod
    def _validate_vector(vector):
        """Validate a generated embedding vector."""

        if not isinstance(vector, (list, tuple)):
            raise TypeError(
                "Embedding vector must be a list or tuple."
            )

        if not vector:
            raise ValueError(
                "Embedding vector cannot be empty."
            )

        for value in vector:
            if not isinstance(value, (int, float)):
                raise TypeError(
                    "Embedding vector values must be numeric."
                )