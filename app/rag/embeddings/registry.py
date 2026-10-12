
"""Registry for RAG embedding-provider implementations."""

from app.rag.interfaces import EmbeddingProvider


class EmbeddingProviderRegistry:
    """Register and retrieve embedding-provider implementations."""

    def __init__(self):
        self._providers = {}
        self._factories = {}

    @staticmethod
    def _normalize_name(name):
        if not isinstance(name, str):
            raise ValueError("Provider name must be a string.")

        normalized = name.strip().lower()

        if not normalized:
            raise ValueError("Provider name must not be empty.")

        return normalized

    @staticmethod
    def _validate_provider_class(provider_class):
        if not isinstance(provider_class, type):
            raise TypeError(
                "Provider must implement EmbeddingProvider."
            )

        if not issubclass(provider_class, EmbeddingProvider):
            raise TypeError(
                "Provider must implement EmbeddingProvider."
            )

    def register(self, name, provider_class):
        normalized = self._normalize_name(name)
        self._validate_provider_class(provider_class)

        if normalized in self._providers:
            raise ValueError(
                f"Provider already registered: {normalized}"
            )

        self._providers[normalized] = provider_class

    def register_factory(self, name, provider_class, factory):
        normalized = self._normalize_name(name)
        self._validate_provider_class(provider_class)

        if not callable(factory):
            raise TypeError("Provider factory must be callable.")

        if normalized in self._providers:
            raise ValueError(
                f"Provider already registered: {normalized}"
            )

        self._providers[normalized] = provider_class
        self._factories[normalized] = factory

    def get(self, name):
        normalized = self._normalize_name(name)
        return self._providers.get(normalized)

    def list_providers(self):
        return list(self._providers.keys())

    def create(self, name, **kwargs):
        normalized = self._normalize_name(name)
        provider_class = self._providers.get(normalized)

        if provider_class is None:
            raise ValueError(
                f"Unknown embedding provider: {name}"
            )

        factory = self._factories.get(normalized)

        if factory is not None:
            provider = factory(**kwargs)
        else:
            provider = provider_class(**kwargs)

        if not isinstance(provider, EmbeddingProvider):
            raise TypeError(
                "Provider factory must return an EmbeddingProvider."
            )

        return provider
