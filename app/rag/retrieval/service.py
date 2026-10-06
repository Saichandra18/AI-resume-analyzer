"""Retrieval service for the RAG subsystem."""

from app.rag.models import RetrievalQuery


class RetrievalService:
    """Coordinate query embedding and vector similarity search."""

    def __init__(self, embedding_provider, vector_store):
        if embedding_provider is None:
            raise ValueError(
                "embedding_provider cannot be None."
            )

        if vector_store is None:
            raise ValueError(
                "vector_store cannot be None."
            )

        if not hasattr(
            embedding_provider,
            "generate_embedding",
        ):
            raise TypeError(
                "embedding_provider must implement "
                "generate_embedding."
            )

        if not hasattr(
            vector_store,
            "search",
        ):
            raise TypeError(
                "vector_store must implement search."
            )

        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    def retrieve(self, query):
        """Retrieve the most relevant chunks for a query."""

        if not isinstance(query, RetrievalQuery):
            raise TypeError(
                "query must be a RetrievalQuery."
            )

        query_vector = (
            self.embedding_provider.generate_embedding(
                query.query
            )
        )

        return self.vector_store.search(
            query_vector,
            top_k=query.top_k,
            filters=query.filters,
        )