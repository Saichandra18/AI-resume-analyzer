
"""Knowledge indexing for the RAG pipeline."""

from copy import deepcopy


class KnowledgeIndexer:
    """Index document chunks into an embedding-backed vector store."""

    def __init__(self, embedding_provider, vector_store, chunk_registry):
        if embedding_provider is None:
            raise ValueError("embedding_provider is required.")
        if not hasattr(embedding_provider, "generate_embeddings"):
            raise TypeError(
                "embedding_provider must provide a generate_embeddings method."
            )

        if vector_store is None:
            raise ValueError("vector_store is required.")
        if not hasattr(vector_store, "add"):
            raise TypeError(
                "vector_store must provide an add method."
            )

        if chunk_registry is None:
            raise ValueError("chunk_registry is required.")
        if not hasattr(chunk_registry, "add"):
            raise TypeError(
                "chunk_registry must provide an add method."
            )

        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.chunk_registry = chunk_registry

    def index(self, chunks):
        """Generate embeddings and index document chunks."""

        if chunks is None:
            raise ValueError("chunks are required.")

        if not isinstance(chunks, (list, tuple)):
            raise TypeError("chunks must be a list or tuple.")

        if not chunks:
            return []

        for chunk in chunks:
            if not hasattr(chunk, "chunk_id"):
                raise TypeError(
                    "Each chunk must provide a chunk_id."
                )
            if not hasattr(chunk, "text"):
                raise TypeError(
                    "Each chunk must provide text."
                )

        texts = [chunk.text for chunk in chunks]
        embeddings = self.embedding_provider.generate_embeddings(texts)

        if len(embeddings) != len(chunks):
            raise ValueError(
                "Embedding provider must return one embedding per chunk."
            )

        records = []

        for chunk, embedding in zip(chunks, embeddings):
            records.append(
                {
                    "chunk_id": chunk.chunk_id,
                    "embedding": embedding,
                    "metadata": deepcopy(
                        getattr(chunk, "metadata", {})
                    ),
                }
            )

        self.vector_store.add(records)

        for chunk in chunks:
            self.chunk_registry.add(chunk)

        return [chunk.chunk_id for chunk in chunks]
