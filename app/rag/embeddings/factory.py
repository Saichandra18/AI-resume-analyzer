
"""Factory for creating configured RAG embedding providers."""

from app.rag.config import RAGConfig
from .local import LocalEmbeddingProvider
from .registry import EmbeddingProviderRegistry


DEFAULT_EMBEDDING_PROVIDER = "local"
DEFAULT_EMBEDDING_MODEL = "default"
DEFAULT_EMBEDDING_DIMENSION = 384


def _build_embedding_provider_registry():
    """Build the registry containing built-in embedding providers."""
    registry = EmbeddingProviderRegistry()

    # The deterministic local provider has no model selection.
    # Keep its existing constructor and behavior unchanged.
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

    Legacy configuration objects remain supported. The model setting
    is passed to registered providers, but the built-in deterministic
    local provider intentionally ignores model selection.
    """
    config = config or RAGConfig()

    provider_name = getattr(
        config,
        "embedding_provider",
        DEFAULT_EMBEDDING_PROVIDER,
    )

    model = getattr(
        config,
        "embedding_model",
        DEFAULT_EMBEDDING_MODEL,
    )

    dimension = getattr(
        config,
        "embedding_dimension",
        DEFAULT_EMBEDDING_DIMENSION,
    )

    # The local provider does not support model selection.
    if (
        isinstance(provider_name, str)
        and provider_name.strip().lower()
        == DEFAULT_EMBEDDING_PROVIDER
    ):
        return _EMBEDDING_PROVIDER_REGISTRY.create(
            provider_name,
            dimension=dimension,
        )

    # Forward model selection to other registered providers.
    return _EMBEDDING_PROVIDER_REGISTRY.create(
        provider_name,
        model=model,
        dimension=dimension,
    )
