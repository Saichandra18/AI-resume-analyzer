import pytest

from app.ai.providers import LLMProvider
from app.ai.registry import LLMProviderRegistry


class ConfigurableProvider(LLMProvider):
    def __init__(
        self,
        model=None,
        api_key=None,
        base_url=None,
    ):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url

    def generate(self, prompt: str) -> str:
        return "generated"


def test_registry_can_create_provider_with_kwargs():
    registry = LLMProviderRegistry()

    registry.register(
        "configurable",
        ConfigurableProvider,
    )

    provider = registry.create(
        "configurable",
        model="test-model",
        api_key="test-key",
        base_url="http://localhost",
    )

    assert isinstance(provider, ConfigurableProvider)
    assert isinstance(provider, LLMProvider)
    assert provider.model == "test-model"
    assert provider.api_key == "test-key"
    assert provider.base_url == "http://localhost"


def test_registry_create_is_case_insensitive():
    registry = LLMProviderRegistry()

    registry.register(
        "configurable",
        ConfigurableProvider,
    )

    provider = registry.create(
        "CONFIGURABLE",
        model="test-model",
    )

    assert isinstance(provider, ConfigurableProvider)


def test_registry_create_unknown_provider_fails():
    registry = LLMProviderRegistry()

    with pytest.raises(
        ValueError,
        match="Unknown LLM provider",
    ):
        registry.create("unknown")


def test_registry_rejects_factory_returning_invalid_provider():
    registry = LLMProviderRegistry()

    registry.register_factory(
        "invalid",
        ConfigurableProvider,
        lambda **kwargs: "not-a-provider",
    )

    with pytest.raises(
        TypeError,
        match="must return an LLMProvider",
    ):
        registry.create("invalid")


def test_registry_rejects_factory_returning_none():
    registry = LLMProviderRegistry()

    registry.register_factory(
        "invalid",
        ConfigurableProvider,
        lambda **kwargs: None,
    )

    with pytest.raises(
        TypeError,
        match="must return an LLMProvider",
    ):
        registry.create("invalid")
