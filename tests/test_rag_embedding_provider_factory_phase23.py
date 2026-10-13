"""Tests for the Phase 23 embedding-provider factory."""

import pytest

from app.rag.config import RAGConfig
from app.rag.embeddings.factory import (
    create_embedding_provider,
    get_embedding_provider_registry,
)
from app.rag.embeddings.local import LocalEmbeddingProvider
from app.rag.embeddings.registry import EmbeddingProviderRegistry
from app.rag.interfaces import EmbeddingProvider


class FakeEmbeddingProvider(EmbeddingProvider):
    """Minimal provider used to test registry extensibility."""

    def __init__(self, dimension=16):
        self.dimension = dimension

    def generate_embedding(self, text):
        return [0.0] * self.dimension

    def generate_embeddings(self, texts):
        return [
            self.generate_embedding(text)
            for text in texts
        ]


def test_factory_creates_local_provider_by_default(monkeypatch):
    monkeypatch.delenv("RAG_EMBEDDING_PROVIDER", raising=False)
    monkeypatch.delenv("RAG_EMBEDDING_DIMENSION", raising=False)

    provider = create_embedding_provider(RAGConfig())

    assert isinstance(provider, LocalEmbeddingProvider)
    assert provider.dimension == 384


def test_factory_uses_configured_dimension(monkeypatch):
    monkeypatch.setenv("RAG_EMBEDDING_PROVIDER", "local")
    monkeypatch.setenv("RAG_EMBEDDING_DIMENSION", "128")

    provider = create_embedding_provider(RAGConfig())

    assert provider.dimension == 128
    assert len(provider.generate_embedding("resume")) == 128


def test_factory_rejects_unknown_provider(monkeypatch):
    monkeypatch.setenv(
        "RAG_EMBEDDING_PROVIDER",
        "unknown-provider",
    )

    with pytest.raises(
        ValueError,
        match="Unknown embedding provider",
    ):
        create_embedding_provider(RAGConfig())


def test_factory_supports_legacy_config_without_embedding_fields():
    """Older config objects should use backward-compatible defaults."""

    class LegacyConfig:
        enabled = True

    provider = create_embedding_provider(LegacyConfig())

    assert isinstance(provider, LocalEmbeddingProvider)
    assert provider.dimension == 384


def test_factory_uses_provider_and_dimension_from_config(monkeypatch):
    """Explicit config attributes should override defaults."""

    monkeypatch.delenv("RAG_EMBEDDING_PROVIDER", raising=False)
    monkeypatch.delenv("RAG_EMBEDDING_DIMENSION", raising=False)

    class CustomConfig:
        embedding_provider = "local"
        embedding_dimension = 64

    provider = create_embedding_provider(CustomConfig())

    assert isinstance(provider, LocalEmbeddingProvider)
    assert provider.dimension == 64


def test_registry_normalizes_provider_names():
    registry = EmbeddingProviderRegistry()
    registry.register(" Local ", LocalEmbeddingProvider)

    assert registry.get("local") is LocalEmbeddingProvider
    assert registry.list_providers() == ["local"]


def test_registry_rejects_duplicate_provider():
    registry = EmbeddingProviderRegistry()
    registry.register("local", LocalEmbeddingProvider)

    with pytest.raises(ValueError, match="already registered"):
        registry.register("LOCAL", LocalEmbeddingProvider)


def test_registry_creates_registered_provider():
    registry = EmbeddingProviderRegistry()
    registry.register("local", LocalEmbeddingProvider)

    provider = registry.create("local", dimension=64)

    assert isinstance(provider, LocalEmbeddingProvider)
    assert provider.dimension == 64


def test_registry_creates_custom_provider():
    """The registry should support new provider implementations."""

    registry = EmbeddingProviderRegistry()
    registry.register("custom", FakeEmbeddingProvider)

    provider = registry.create("custom", dimension=24)

    assert isinstance(provider, FakeEmbeddingProvider)
    assert provider.dimension == 24
    assert len(provider.generate_embedding("test")) == 24


def test_registry_rejects_unknown_provider():
    registry = EmbeddingProviderRegistry()

    with pytest.raises(ValueError, match="Unknown embedding provider"):
        registry.create("missing")


def test_registry_rejects_invalid_provider_class():
    registry = EmbeddingProviderRegistry()

    with pytest.raises(TypeError, match="EmbeddingProvider"):
        registry.register("invalid", dict)


def test_registry_rejects_non_callable_factory():
    registry = EmbeddingProviderRegistry()

    with pytest.raises(TypeError, match="callable"):
        registry.register_factory(
            "local",
            LocalEmbeddingProvider,
            None,
        )


def test_registry_rejects_factory_returning_invalid_object():
    """A factory must return an EmbeddingProvider instance."""

    registry = EmbeddingProviderRegistry()
    registry.register_factory(
        "invalid-result",
        FakeEmbeddingProvider,
        lambda **kwargs: object(),
    )

    with pytest.raises(
        TypeError,
        match="must return an EmbeddingProvider",
    ):
        registry.create("invalid-result")


@pytest.mark.parametrize(
    "name",
    ["", "   "],
)
def test_registry_rejects_blank_provider_names(name):
    registry = EmbeddingProviderRegistry()

    with pytest.raises(ValueError, match="must not be empty"):
        registry.get(name)


@pytest.mark.parametrize(
    "name",
    [None, 123, [], {}],
)
def test_registry_rejects_non_string_provider_names(name):
    registry = EmbeddingProviderRegistry()

    with pytest.raises(ValueError, match="must be a string"):
        registry.get(name)


def test_registry_rejects_duplicate_factory_registration():
    registry = EmbeddingProviderRegistry()
    registry.register_factory(
        "custom",
        FakeEmbeddingProvider,
        lambda **kwargs: FakeEmbeddingProvider(**kwargs),
    )

    with pytest.raises(ValueError, match="already registered"):
        registry.register_factory(
            "CUSTOM",
            FakeEmbeddingProvider,
            lambda **kwargs: FakeEmbeddingProvider(**kwargs),
        )


def test_shared_registry_contains_local_provider():
    registry = get_embedding_provider_registry()

    assert registry.get("local") is LocalEmbeddingProvider


def test_factory_passes_configured_model_to_custom_provider(
    monkeypatch,
):
    """Custom providers receive the configured model and dimension."""

    class ModelAwareEmbeddingProvider(EmbeddingProvider):
        def __init__(self, model="default", dimension=16):
            self.model = model
            self.dimension = dimension

        def generate_embedding(self, text):
            return [0.0] * self.dimension

        def generate_embeddings(self, texts):
            return [
                self.generate_embedding(text)
                for text in texts
            ]

    registry = get_embedding_provider_registry()
    provider_name = "phase24_model_aware_test"

    if registry.get(provider_name) is None:
        registry.register_factory(
            provider_name,
            ModelAwareEmbeddingProvider,
            lambda **kwargs: ModelAwareEmbeddingProvider(
                model=kwargs.get("model", "default"),
                dimension=kwargs.get("dimension", 16),
            ),
        )

    class CustomConfig:
        embedding_provider = provider_name
        embedding_model = "test-embedding-model"
        embedding_dimension = 48

    provider = create_embedding_provider(CustomConfig())

    assert isinstance(provider, ModelAwareEmbeddingProvider)
    assert provider.model == "test-embedding-model"
    assert provider.dimension == 48
