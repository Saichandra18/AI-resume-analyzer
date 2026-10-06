"""Provider interfaces for the RAG subsystem."""

from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """Abstract interface for generating text embeddings."""

    @abstractmethod
    def generate_embedding(self, text):
        """Generate an embedding for a single text value."""

    @abstractmethod
    def generate_embeddings(self, texts):
        """Generate embeddings for multiple text values."""


class VectorStore(ABC):
    """Abstract interface for vector storage and similarity search."""

    @abstractmethod
    def add(self, records):
        """Add embedding records to the vector store."""

    @abstractmethod
    def search(self, query_vector, top_k=5, filters=None):
        """Search for the most relevant vectors."""

    @abstractmethod
    def delete(self, chunk_ids):
        """Delete records identified by chunk IDs."""

    @abstractmethod
    def count(self):
        """Return the number of stored records."""