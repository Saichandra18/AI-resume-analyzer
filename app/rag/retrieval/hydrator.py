"""Hydrate retrieved RAG chunks with their original document content."""

from app.rag.models import RetrievedChunk


class RetrievalHydrator:
    """Attach original chunk text and metadata to retrieval results."""

    def __init__(self, chunk_registry):
        if chunk_registry is None:
            raise ValueError("chunk_registry is required.")

        if not hasattr(chunk_registry, "get"):
            raise TypeError(
                "chunk_registry must provide a get method."
            )

        self.chunk_registry = chunk_registry

    def hydrate(self, retrieved_chunks):
        """Hydrate retrieved chunks using the chunk registry."""

        if not isinstance(retrieved_chunks, (list, tuple)):
            raise TypeError(
                "retrieved_chunks must be a list or tuple."
            )

        hydrated = []

        for retrieved in retrieved_chunks:
            if not isinstance(retrieved, RetrievedChunk):
                raise TypeError(
                    "All retrieved chunks must be "
                    "RetrievedChunk instances."
                )

            chunk = self.chunk_registry.get(
                retrieved.chunk_id
            )

            if chunk is None:
                continue

            hydrated.append(
                RetrievedChunk(
                    chunk_id=retrieved.chunk_id,
                    text=chunk.text,
                    score=retrieved.score,
                    document_id=chunk.document_id,
                    metadata=dict(chunk.metadata),
                )
            )

        return hydrated