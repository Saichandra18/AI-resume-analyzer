import pytest

from app.ai.factory import create_llm_provider
from app.ai.providers import (
    LLMProviderType,
    LocalProvider,
    OpenAICompatibleProvider,
    OpenAIProvider,
)


def test_openai_configuration_requires_api_key(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(
        ValueError,
        match="OPENAI_API_KEY is not configured",
    ):
        create_llm_provider()


def test_openai_configuration_uses_explicit_llm_api_key(
    monkeypatch,
):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    monkeypatch.setenv(
        "LLM_API_KEY",
        "explicit-test-key",
    )
    monkeypatch.delenv(
        "OPENAI_API_KEY",
        raising=False,
    )

    provider = create_llm_provider()

    assert isinstance(provider, OpenAIProvider)
    assert provider.api_key == "explicit-test-key"


def test_openai_compatible_requires_api_key(monkeypatch):
    monkeypatch.setenv(
        "LLM_PROVIDER",
        "openai_compatible",
    )
    monkeypatch.setenv(
        "LLM_MODEL",
        "compatible-model",
    )
    monkeypatch.setenv(
        "LLM_BASE_URL",
        "https://example.test/v1",
    )
    monkeypatch.delenv(
        "LLM_API_KEY",
        raising=False,
    )

    with pytest.raises(
        ValueError,
        match="API key is not configured",
    ):
        create_llm_provider()


def test_openai_compatible_requires_base_url(monkeypatch):
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
    monkeypatch.delenv(
        "LLM_BASE_URL",
        raising=False,
    )

    with pytest.raises(
        ValueError,
        match="Base URL must not be empty",
    ):
        create_llm_provider()


def test_local_provider_does_not_require_api_key(monkeypatch):
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
    monkeypatch.delenv(
        "OPENAI_API_KEY",
        raising=False,
    )

    provider = create_llm_provider()

    assert isinstance(provider, LocalProvider)
    assert provider.api_key is None


def test_local_provider_does_not_inherit_openai_api_key(
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
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "should-not-be-used",
    )

    provider = create_llm_provider()

    assert isinstance(provider, LocalProvider)
    assert provider.api_key is None


def test_local_provider_requires_base_url(monkeypatch):
    monkeypatch.setenv(
        "LLM_PROVIDER",
        "local",
    )
    monkeypatch.setenv(
        "LLM_MODEL",
        "local-model",
    )
    monkeypatch.delenv(
        "LLM_BASE_URL",
        raising=False,
    )

    with pytest.raises(
        ValueError,
        match="Base URL must not be empty",
    ):
        create_llm_provider()


def test_provider_requires_model(monkeypatch):
    monkeypatch.setenv(
        "LLM_PROVIDER",
        "local",
    )
    monkeypatch.delenv(
        "LLM_MODEL",
        raising=False,
    )
    monkeypatch.delenv(
        "OPENAI_MODEL",
        raising=False,
    )
    monkeypatch.setenv(
        "LLM_BASE_URL",
        "http://localhost:11434/v1",
    )

    with pytest.raises(
        ValueError,
        match="Model must not be empty",
    ):
        create_llm_provider()


def test_invalid_provider_is_rejected(monkeypatch):
    monkeypatch.setenv(
        "LLM_PROVIDER",
        "unsupported-provider",
    )
    monkeypatch.setenv(
        "LLM_MODEL",
        "test-model",
    )

    with pytest.raises(
        ValueError,
        match="Unsupported LLM provider",
    ):
        create_llm_provider()


def test_provider_type_values_are_stable():
    assert LLMProviderType.OPENAI.value == "openai"
    assert (
        LLMProviderType.OPENAI_COMPATIBLE.value
        == "openai_compatible"
    )
    assert LLMProviderType.LOCAL.value == "local"


def test_openai_compatible_does_not_require_openai_api_key(
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
        "https://example.test/v1",
    )
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "different-key",
    )

    provider = create_llm_provider()

    assert isinstance(
        provider,
        OpenAICompatibleProvider,
    )
    assert provider.api_key == "compatible-key"
    assert provider.api_key != "different-key"
