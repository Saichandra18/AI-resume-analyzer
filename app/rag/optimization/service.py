
"""Service entry point for RAG-assisted resume optimization."""

from copy import deepcopy

from app.rag.config import RAGConfig
from app.rag.embeddings.factory import create_embedding_provider
from app.rag.optimization.knowledge_guidance import (
    KnowledgeGuidanceAdapter,
)
from app.rag.optimization.orchestrator import (
    RAGOptimizationOrchestrator,
)
from app.rag.optimization.resume_context import (
    ResumeContextBuilder,
)
from app.rag.retrieval.hydrator import RetrievalHydrator
from app.rag.retrieval.jd_retriever import JDAwareRetriever
from app.rag.retrieval.service import RetrievalService
from app.rag.vectorstore.in_memory import InMemoryVectorStore
from app.rag.vectorstore.registry import ChunkRegistry


class RAGOptimizationService:
    """Coordinate RAG retrieval and optimization support."""

    def __init__(
        self,
        config=None,
        embedding_provider=None,
        vector_store=None,
        chunk_registry=None,
        retrieval_service=None,
        retriever=None,
        orchestrator=None,
        resume_context_builder=None,
        knowledge_base_service=None,
        knowledge_guidance_adapter=None,
    ):
        self.config = config or RAGConfig()

        self.enabled = bool(
            getattr(self.config, "enabled", False)
        )

        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.chunk_registry = chunk_registry
        self.retrieval_service = retrieval_service
        self.retriever = retriever
        self.orchestrator = orchestrator

        self.resume_context_builder = (
            resume_context_builder
            or ResumeContextBuilder()
        )

        self.knowledge_base_service = (
            knowledge_base_service
        )

        self.knowledge_guidance_adapter = (
            knowledge_guidance_adapter
            or KnowledgeGuidanceAdapter()
        )

        if self.orchestrator is not None:
            self._validate_orchestrator(
                self.orchestrator
            )

        if not self.enabled:
            return

        self._initialize_runtime()

    @staticmethod
    def _validate_orchestrator(orchestrator):
        """Validate an injected orchestrator."""

        if not hasattr(orchestrator, "optimize"):
            raise TypeError(
                "orchestrator must implement optimize."
            )

    def _is_enabled(self):
        """Return whether RAG optimization is enabled."""
        return self.enabled

    def _initialize_runtime(self):
        """Initialize missing RAG runtime dependencies."""

        if self.embedding_provider is None:
            self.embedding_provider = create_embedding_provider(
                config=self.config
            )

        if self.vector_store is None:
            self.vector_store = InMemoryVectorStore()

        if self.chunk_registry is None:
            self.chunk_registry = ChunkRegistry()

        if self.retrieval_service is None:
            self.retrieval_service = RetrievalService(
                embedding_provider=self.embedding_provider,
                vector_store=self.vector_store,
            )

        if self.retriever is None:
            hydrator = RetrievalHydrator(
                self.chunk_registry
            )

            self.retriever = JDAwareRetriever(
                retrieval_service=self.retrieval_service,
                hydrator=hydrator,
                resume_context_builder=self.resume_context_builder,
            )

        if self.orchestrator is None:
            self.orchestrator = RAGOptimizationOrchestrator(
                retriever=self.retriever
            )

        self._validate_orchestrator(
            self.orchestrator
        )

    @staticmethod
    def _validate_jd_analysis(jd_analysis):
        """Validate the job-description analysis."""

        if jd_analysis is None:
            raise ValueError(
                "jd_analysis is required."
            )

        if not isinstance(jd_analysis, dict):
            raise TypeError(
                "jd_analysis must be a dictionary."
            )

    @staticmethod
    def _empty_phase11_payload():
        """Return the disabled/empty Phase 11 payload."""

        return {
            "skills_to_emphasize": [],
            "experience_to_emphasize": [],
            "keywords_to_emphasize": [],
            "emphasis_instructions": [],
            "grounding": [],
            "metadata": {
                "rag_enabled": False,
            },
        }

    @staticmethod
    def _empty_knowledge_context():
        """Return an empty knowledge-base context."""

        return {
            "enabled": False,
            "retrieved_chunks": [],
            "count": 0,
            "metadata": {
                "knowledge_base": False,
                "indexed_count": 0,
            },
        }

    def _retrieve_knowledge_context(self, jd_analysis):
        """Retrieve and adapt general optimization guidance."""

        if self.knowledge_base_service is None:
            return self._empty_knowledge_context()

        if not hasattr(
            self.knowledge_base_service,
            "retrieve",
        ):
            raise TypeError(
                "knowledge_base_service must implement retrieve."
            )

        results = self.knowledge_base_service.retrieve(
            jd_analysis
        )

        if not isinstance(results, (list, tuple)):
            raise TypeError(
                "knowledge_base_service.retrieve "
                "must return a list or tuple."
            )

        indexed_count = 0

        if hasattr(
            self.knowledge_base_service,
            "indexed_count",
        ):
            indexed_count = (
                self.knowledge_base_service.indexed_count()
            )

        guidance_context = (
            self.knowledge_guidance_adapter.build(
                results,
                metadata={
                    "indexed_count": indexed_count,
                },
            )
        )

        return {
            "enabled": True,
            "retrieved_chunks": list(results),
            "count": len(results),
            "guidance": guidance_context["guidance"],
            "metadata": guidance_context["metadata"],
        }

    def optimize(self, jd_analysis, resume_data=None):
        """Run RAG-assisted optimization when enabled."""

        self._validate_jd_analysis(jd_analysis)

        if not self._is_enabled():
            return {
                "enabled": False,
                "retrieved_chunks": [],
                "evidence": [],
                "recommendations": [],
                "safety_results": [],
                "signals": None,
                "phase11_payload": self._empty_phase11_payload(),
                "knowledge_context": self._empty_knowledge_context(),
                "metadata": {
                    "rag_enabled": False,
                    "resume_context_available": (
                        resume_data is not None
                    ),
                },
            }

        self._initialize_runtime()

        resume_context = None

        if resume_data is not None:
            resume_context = (
                self.resume_context_builder.build(
                    resume_data
                )
            )

        if resume_context is None:
            result = self.orchestrator.optimize(
                jd_analysis
            )
        else:
            try:
                result = self.orchestrator.optimize(
                    jd_analysis,
                    resume_context=resume_context,
                )
            except TypeError as exc:
                if "resume_context" not in str(exc):
                    raise

                result = self.orchestrator.optimize(
                    jd_analysis
                )

        if not isinstance(result, dict):
            raise TypeError(
                "RAG optimization orchestrator "
                "must return a dictionary."
            )

        if "phase11_payload" not in result:
            raise TypeError(
                "RAG optimization result must "
                "contain phase11_payload."
            )

        result = deepcopy(result)

        knowledge_context = (
            self._retrieve_knowledge_context(
                jd_analysis
            )
        )

        result["knowledge_context"] = knowledge_context

        result.setdefault("enabled", True)
        result.setdefault("metadata", {})

        result["metadata"].setdefault(
            "rag_enabled",
            True,
        )

        result["metadata"].setdefault(
            "resume_context_available",
            resume_context is not None,
        )

        result["metadata"].setdefault(
            "knowledge_base_enabled",
            self.knowledge_base_service is not None,
        )

        return result

    def index_chunks(self, chunks):
        """Index document chunks into the service runtime."""

        if not self._is_enabled():
            return []

        self._initialize_runtime()

        from app.rag.indexing.indexer import KnowledgeIndexer

        indexer = KnowledgeIndexer(
            embedding_provider=self.embedding_provider,
            vector_store=self.vector_store,
            chunk_registry=self.chunk_registry,
        )

        return indexer.index(chunks)

    def count_indexed_chunks(self):
        """Return the number of indexed vector records."""

        if not self._is_enabled():
            return 0

        self._initialize_runtime()

        return self.vector_store.count()

    def get_phase11_payload(
        self,
        jd_analysis,
        resume_data=None,
    ):
        """Return a defensive copy of the Phase 11 payload."""

        self._validate_jd_analysis(jd_analysis)

        result = self.optimize(
            jd_analysis=jd_analysis,
            resume_data=resume_data,
        )

        payload = result.get("phase11_payload")

        if payload is None:
            raise TypeError(
                "RAG optimization result must "
                "contain phase11_payload."
            )

        return deepcopy(payload)
