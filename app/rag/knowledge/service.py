"""Runtime service for the RAG knowledge base."""

from copy import deepcopy

from app.rag.embeddings.factory import create_embedding_provider
from app.rag.indexing import (
    KnowledgeIndexer,
    KnowledgeIndexingPipeline,
)
from app.rag.knowledge.catalog import DefaultKnowledgeCatalog
from app.rag.knowledge.manager import KnowledgeBaseManager
from app.rag.retrieval import KnowledgeRetriever
from app.rag.vectorstore.in_memory import InMemoryVectorStore
from app.rag.vectorstore.persistence import VectorStorePersistence
from app.rag.vectorstore.registry import ChunkRegistry


class KnowledgeBaseService:
    """Build, index, persist, and retrieve approved knowledge."""

    def __init__(
        self,
        embedding_provider=None,
        vector_store=None,
        chunk_registry=None,
        retrieval_service=None,
        catalog=None,
        indexing_pipeline=None,
        persistence=None,
        retriever=None,
        top_k=5,
    ):
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.chunk_registry = chunk_registry
        self.retrieval_service = retrieval_service
        self.catalog = catalog
        self.indexing_pipeline = indexing_pipeline
        self.persistence = persistence
        self.retriever = retriever
        self.top_k = top_k

        self._initialize_runtime()

    def _initialize_runtime(self):
        """Initialize missing knowledge-base dependencies."""

        if self.embedding_provider is None:
            self.embedding_provider = create_embedding_provider()

        if self.chunk_registry is None:
            self.chunk_registry = ChunkRegistry()

        if self.vector_store is None:
            self.vector_store = InMemoryVectorStore(
                chunk_registry=self.chunk_registry
            )

        if self.retrieval_service is None:
            from app.rag.retrieval.service import RetrievalService

            self.retrieval_service = RetrievalService(
                embedding_provider=self.embedding_provider,
                vector_store=self.vector_store,
            )

        if self.catalog is None:
            self.catalog = DefaultKnowledgeCatalog().build()

        if self.indexing_pipeline is None:
            indexer = KnowledgeIndexer(
                embedding_provider=self.embedding_provider,
                vector_store=self.vector_store,
                chunk_registry=self.chunk_registry,
            )

            self.indexing_pipeline = KnowledgeIndexingPipeline(
                indexer=indexer
            )

        if self.persistence is None:
            self.persistence = VectorStorePersistence(
                vector_store=self.vector_store,
                chunk_registry=self.chunk_registry,
            )

        if self.retriever is None:
            self.retriever = KnowledgeRetriever(
                retrieval_service=self.retrieval_service,
                top_k=self.top_k,
            )

        self.manager = KnowledgeBaseManager(
            catalog=self.catalog,
            indexing_pipeline=self.indexing_pipeline,
            persistence=self.persistence,
        )

    def index_all(self):
        """Index all approved knowledge sources."""
        return self.manager.index_all()

    def index_source(self, source_id):
        """Index one approved knowledge source."""
        return self.manager.index_source(source_id)

    def retrieve(self, jd_analysis):
        """Retrieve general knowledge relevant to a JD."""
        return self.retriever.retrieve(jd_analysis)

    def save(self, file_path):
        """Persist the current knowledge index."""
        return self.manager.save(file_path)

    def load(self, file_path):
        """Load a persisted knowledge index."""
        return self.manager.load(file_path)

    def indexed_count(self):
        """Return the number of indexed knowledge records."""
        return self.manager.indexed_count()

    def source_status(self):
        """Return status information for approved sources."""
        return self.manager.source_status()

    def is_indexed(self):
        """Return whether the knowledge base contains records."""
        return self.indexed_count() > 0

    def retrieve_with_metadata(self, jd_analysis):
        """Retrieve knowledge and attach service-level metadata."""
        results = self.retrieve(jd_analysis)

        return {
            "retrieved_chunks": list(results),
            "count": len(results),
            "indexed_count": self.indexed_count(),
            "metadata": {
                "knowledge_base": True,
                "indexed_count": self.indexed_count(),
            },
        }
