"""Registry for document chunks used during RAG retrieval hydration."""

from app.rag.models import DocumentChunk


class ChunkRegistry:
    """Store document chunks by chunk ID."""

    def __init__(self):
        self._chunks = {}

    def add(self, chunks):
        """Register one or more document chunks."""

        if isinstance(chunks, DocumentChunk):
            chunks = [chunks]

        elif isinstance(chunks, (list, tuple)):
            chunks = list(chunks)

        else:
            raise TypeError(
                "chunks must be a DocumentChunk, list, or tuple."
            )

        for chunk in chunks:
            if not isinstance(chunk, DocumentChunk):
                raise TypeError(
                    "All chunks must be DocumentChunk instances."
                )

            self._chunks[chunk.chunk_id] = chunk

    def get(self, chunk_id):
        """Return a registered chunk by ID."""
        return self._chunks.get(chunk_id)

    def remove(self, chunk_id):
        """Remove a chunk by ID if present."""
        return self._chunks.pop(chunk_id, None)

    def clear(self):
        """Remove all registered chunks."""
        self._chunks.clear()

    def count(self):
        """Return the number of registered chunks."""
        return len(self._chunks)

    def contains(self, chunk_id):
        """Return whether a chunk ID is registered."""
        return chunk_id in self._chunks

    def delete(self, chunk_ids):
        """Delete one or more chunks from the registry."""

        if not isinstance(chunk_ids, (list, tuple)):
            raise TypeError(
                "chunk_ids must be a list or tuple."
            )

        for chunk_id in chunk_ids:
            self._chunks.pop(chunk_id, None)