"""Factory for creating configured RAG embedding providers."""

from app.rag.config import RAGConfig
from .local import LocalEmbeddingProvider
from .registry import EmbeddingProviderRegistry


DEFAULT_EMBEDDING_PROVIDER = "local"
DEFAULT_EMBEDDING_DIMENSION = 384


def _build_embedding_provider_registry():
    """Build the registry containing built-in embedding providers."""
    registry = EmbeddingProviderRegistry()

    registry.register_factory(
        DEFAULT_EMBEDDING_PROVIDER,
        LocalEmbeddingProvider,
        lambda **kwargs: LocalEmbeddingProvider(
            dimension=kwargs.get(
                "dimension",
                DEFAULT_EMBEDDING_DIMENSION,
            )
        ),
    )

    return registry


_EMBEDDING_PROVIDER_REGISTRY = _build_embedding_provider_registry()


def get_embedding_provider_registry():
    """Return the shared embedding-provider registry."""
    return _EMBEDDING_PROVIDER_REGISTRY


def create_embedding_provider(config=None):
    """Create an embedding provider from RAG configuration.

    Older configuration objects that only expose the previous RAG
    settings remain supported. Missing embedding settings fall back
    to the established local provider and 384-dimensional embeddings.
    """
    config = config or RAGConfig()

    provider_name = getattr(
        config,
        "embedding_provider",
        DEFAULT_EMBEDDING_PROVIDER,
    )

    dimension = getattr(
        config,
        "embedding_dimension",
        DEFAULT_EMBEDDING_DIMENSION,
    )

    return _EMBEDDING_PROVIDER_REGISTRY.create(
        provider_name,
        dimension=dimension,
    )
