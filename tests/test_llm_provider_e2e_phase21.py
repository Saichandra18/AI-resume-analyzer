import pytest

from app.ai.factory import create_llm_provider
from app.ai.fallback import FallbackLLMProvider
from app.ai.providers import (
    LLMProvider,
    LLMProviderType,
    LocalProvider,
    OpenAICompatibleProvider,
    OpenAIProvider,
)


class FakeProvider(LLMProvider):
    def __init__(self, result="generated"):
        self.result = result
        self.calls = []

    def generate(self, prompt: str) -> str:
        self.calls.append(prompt)
        return self.result


class FailingProvider(LLMProvider):
    def __init__(self, error):
        self.error = error
        self.calls = []

    def generate(self, prompt: str) -> str:
        self.calls.append(prompt)
        raise self.error


def test_factory_selects_openai_provider(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    provider = create_llm_provider()

    assert isinstance(provider, OpenAIProvider)
    assert provider.model == "test-model"


def test_factory_selects_openai_compatible_provider(monkeypatch):
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
        "https://example.test/v1",
    )

    provider = create_llm_provider()

    assert isinstance(
        provider,
        OpenAICompatibleProvider,
    )
    assert provider.model == "compatible-model"
    assert provider.base_url == "https://example.test/v1"


def test_factory_selects_local_provider(monkeypatch):
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

    provider = create_llm_provider()

    assert isinstance(provider, LocalProvider)
    assert provider.model == "local-model"
    assert provider.base_url == (
        "http://localhost:11434/v1"
    )


def test_runtime_switching_changes_provider_type(monkeypatch):
    monkeypatch.setenv(
        "LLM_MODEL",
        "test-model",
    )
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "test-key",
    )

    monkeypatch.setenv(
        "LLM_PROVIDER",
        "openai",
    )

    openai_provider = create_llm_provider()

    monkeypatch.setenv(
        "LLM_PROVIDER",
        "local",
    )
    monkeypatch.setenv(
        "LLM_BASE_URL",
        "http://localhost:11434/v1",
    )

    local_provider = create_llm_provider()

    assert isinstance(
        openai_provider,
        OpenAIProvider,
    )
    assert isinstance(
        local_provider,
        LocalProvider,
    )
    assert type(openai_provider) is not type(local_provider)


def test_all_providers_share_common_interface():
    providers = [
        FakeProvider(),
    ]

    for provider in providers:
        assert isinstance(provider, LLMProvider)
        assert callable(provider.generate)


def test_application_can_use_substitutable_provider():
    provider = FakeProvider(
        "provider generated resume"
    )

    result = provider.generate(
        "Generate an optimized resume."
    )

    assert result == "provider generated resume"
    assert provider.calls == [
        "Generate an optimized resume."
    ]


def test_fallback_can_switch_between_provider_types():
    primary = FailingProvider(
        RuntimeError("Primary unavailable")
    )
    fallback = FakeProvider(
        "Fallback generated resume"
    )

    provider = FallbackLLMProvider(
        primary=primary,
        fallback=fallback,
    )

    result = provider.generate(
        "Generate resume."
    )

    assert result == "Fallback generated resume"
    assert primary.calls == ["Generate resume."]
    assert fallback.calls == ["Generate resume."]


def test_fallback_provider_is_itself_an_llm_provider():
    primary = FakeProvider("primary")
    fallback = FakeProvider("fallback")

    provider = FallbackLLMProvider(
        primary=primary,
        fallback=fallback,
    )

    assert isinstance(provider, LLMProvider)
    assert callable(provider.generate)


def test_provider_switching_requires_no_application_logic():
    providers = [
        FakeProvider("openai output"),
        FakeProvider("compatible output"),
        FakeProvider("local output"),
    ]

    prompts = [
        "Generate resume.",
        "Improve summary.",
        "Optimize skills.",
    ]

    for provider in providers:
        assert isinstance(provider, LLMProvider)

        for prompt in prompts:
            result = provider.generate(prompt)

            assert result
            assert provider.calls[-1] == prompt


def test_complete_provider_chain():
    primary = FailingProvider(
        RuntimeError("Primary provider failed")
    )
    fallback = FakeProvider(
        "final generated output"
    )

    provider = FallbackLLMProvider(
        primary=primary,
        fallback=fallback,
    )

    result = provider.generate(
        "Create final optimized resume."
    )

    assert result == "final generated output"
    assert len(primary.calls) == 1
    assert len(fallback.calls) == 1
