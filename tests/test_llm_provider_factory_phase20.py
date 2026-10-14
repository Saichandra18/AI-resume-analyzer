import pytest

from app.ai.factory import create_llm_provider
from app.ai.providers import (
    LLMProvider,
    LocalProvider,
    OpenAICompatibleProvider,
    OpenAIProvider,
)


def test_factory_creates_openai_provider(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    monkeypatch.setenv("LLM_API_KEY", "test-key")

    provider = create_llm_provider()

    assert isinstance(provider, OpenAIProvider)
    assert isinstance(provider, LLMProvider)
    assert provider.model == "test-model"
    assert provider.api_key == "test-key"


def test_factory_supports_legacy_openai_environment(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("LLM_MODEL", raising=False)
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    monkeypatch.setenv("OPENAI_MODEL", "legacy-model")
    monkeypatch.setenv("OPENAI_API_KEY", "legacy-key")

    provider = create_llm_provider()

    assert isinstance(provider, OpenAIProvider)
    assert provider.model == "legacy-model"
    assert provider.api_key == "legacy-key"


def test_factory_creates_openai_compatible_provider(
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
    assert isinstance(provider, LLMProvider)
    assert provider.model == "compatible-model"
    assert provider.api_key == "compatible-key"
    assert provider.base_url == "http://localhost:1234/v1"


def test_factory_creates_local_provider(
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
    assert isinstance(provider, LLMProvider)
    assert provider.model == "local-model"
    assert provider.base_url == "http://localhost:11434/v1"
    assert provider.api_key is None


@pytest.mark.parametrize(
    "provider_name",
    [
        "unsupported",
        "gemini",
    ],
)
def test_factory_rejects_unknown_providers(
    monkeypatch,
    provider_name,
):
    monkeypatch.setenv(
        "LLM_PROVIDER",
        provider_name,
    )
    monkeypatch.setenv(
        "LLM_MODEL",
        "test-model",
    )

    with pytest.raises(
        ValueError,
        match=f"Unsupported LLM provider: {provider_name}",
    ):
        create_llm_provider()