import pytest

from app.ai.factory import create_llm_provider
from app.ai.providers import (
    LLMProvider,
    LocalProvider,
    OpenAICompatibleProvider,
    OpenAIProvider,
)


def test_existing_openai_provider_is_available_through_dynamic_registry(
    monkeypatch,
):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    monkeypatch.setenv("LLM_API_KEY", "test-key")

    provider = create_llm_provider()

    assert isinstance(provider, OpenAIProvider)
    assert isinstance(provider, LLMProvider)


def test_existing_openai_compatible_provider_is_available_through_dynamic_registry(
    monkeypatch,
):
    monkeypatch.setenv(
        "LLM_PROVIDER",
        "openai_compatible",
    )
    monkeypatch.setenv(
        "LLM_MODEL",
        "compatible-model",
    )
    monkeypatch.setenv(
        "LLM_API_KEY",
        "compatible-key",
    )
    monkeypatch.setenv(
        "LLM_BASE_URL",
        "http://localhost:1234/v1",
    )

    provider = create_llm_provider()

    assert isinstance(
        provider,
        OpenAICompatibleProvider,
    )


def test_existing_local_provider_is_available_through_dynamic_registry(
    monkeypatch,
):
    monkeypatch.setenv(
        "LLM_PROVIDER",
        "local",
    )
    monkeypatch.setenv(
        "LLM_MODEL",
        "local-model",
    )
    monkeypatch.setenv(
        "LLM_BASE_URL",
        "http://localhost:11434/v1",
    )
    monkeypatch.delenv(
        "LLM_API_KEY",
        raising=False,
    )

    provider = create_llm_provider()

    assert isinstance(provider, LocalProvider)


def test_dynamic_provider_registry_can_be_extended_without_factory_changes():
    from app.ai.registry import LLMProviderRegistry

    class CustomProvider(LLMProvider):
        def __init__(self, model=None):
            self.model = model

        def generate(self, prompt: str) -> str:
            return "custom"

    registry = LLMProviderRegistry()

    registry.register(
        "custom",
        CustomProvider,
    )

    provider_class = registry.get("custom")

    provider = provider_class(
        model="custom-model",
    )

    assert isinstance(provider, CustomProvider)
    assert provider.model == "custom-model"


def test_registry_remains_vendor_agnostic():
    from app.ai.registry import LLMProviderRegistry

    class ProviderOne(LLMProvider):
        def generate(self, prompt: str) -> str:
            return "one"

    class ProviderTwo(LLMProvider):
        def generate(self, prompt: str) -> str:
            return "two"

    registry = LLMProviderRegistry()

    registry.register("provider-one", ProviderOne)
    registry.register("provider-two", ProviderTwo)

    assert registry.list_providers() == [
        "provider-one",
        "provider-two",
    ]

def test_application_registry_can_register_custom_provider():
    from app.ai.factory import get_provider_registry

    class CustomProvider(LLMProvider):
        def __init__(self, model=None):
            self.model = model

        def generate(self, prompt: str) -> str:
            return "custom"

    registry = get_provider_registry()

    registry.register(
        "phase22_test_custom",
        CustomProvider,
    )

    provider = registry.create(
        "phase22_test_custom",
        model="custom-model",
    )

    assert isinstance(provider, CustomProvider)
    assert provider.model == "custom-model"
    assert provider.generate("Hello") == "custom"

def test_registered_custom_provider_can_be_selected_at_runtime(
    monkeypatch,
):
    from app.ai.factory import (
        create_llm_provider,
        get_provider_registry,
    )

    class CustomRuntimeProvider(LLMProvider):
        def __init__(self, model=None):
            self.model = model

        def generate(self, prompt: str) -> str:
            return f"Custom response: {prompt}"

    provider_name = "phase22_custom_runtime_selection"
    registry = get_provider_registry()

    if registry.get(provider_name) is None:
        registry.register(provider_name, CustomRuntimeProvider)

    monkeypatch.setenv("LLM_PROVIDER", provider_name)
    monkeypatch.setenv("LLM_MODEL", "custom-test-model")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("LLM_BASE_URL", raising=False)

    provider = create_llm_provider()

    assert isinstance(provider, CustomRuntimeProvider)
    assert provider.model == "custom-test-model"
    assert provider.generate("Hello") == "Custom response: Hello"