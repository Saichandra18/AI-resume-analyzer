import pytest

from app.ai.providers import (
    LLMConfig,
    LLMProviderType,
    get_llm_config,
)


def test_provider_types_are_defined():
    assert LLMProviderType.OPENAI.value == "openai"
    assert LLMProviderType.OPENAI_COMPATIBLE.value == "openai_compatible"
    assert LLMProviderType.LOCAL.value == "local"


def test_llm_config_stores_provider_configuration():
    config = LLMConfig(
        provider=LLMProviderType.OPENAI,
        model="gpt-test",
        api_key="test-key",
        base_url="https://example.com/v1",
    )

    assert config.provider is LLMProviderType.OPENAI
    assert config.model == "gpt-test"
    assert config.api_key == "test-key"
    assert config.base_url == "https://example.com/v1"


def test_llm_config_allows_optional_connection_values():
    config = LLMConfig(
        provider=LLMProviderType.LOCAL,
        model="local-model",
    )

    assert config.provider is LLMProviderType.LOCAL
    assert config.model == "local-model"
    assert config.api_key is None
    assert config.base_url is None


def test_llm_config_rejects_empty_model():
    with pytest.raises(ValueError, match="Model must not be empty"):
        LLMConfig(
            provider=LLMProviderType.OPENAI,
            model="",
        )


def test_llm_config_rejects_invalid_provider():
    with pytest.raises(ValueError, match="Provider must be a valid"):
        LLMConfig(
            provider="invalid",
            model="test-model",
        )


def test_get_llm_config_uses_generic_environment_variables(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_BASE_URL", "https://example.com/v1")

    config = get_llm_config()

    assert config.provider is LLMProviderType.OPENAI
    assert config.model == "test-model"
    assert config.api_key == "test-key"
    assert config.base_url == "https://example.com/v1"


def test_get_llm_config_preserves_openai_environment_compatibility(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("LLM_MODEL", raising=False)
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("LLM_BASE_URL", raising=False)

    monkeypatch.setenv("OPENAI_MODEL", "legacy-model")
    monkeypatch.setenv("OPENAI_API_KEY", "legacy-key")

    config = get_llm_config()

    assert config.provider is LLMProviderType.OPENAI
    assert config.model == "legacy-model"
    assert config.api_key == "legacy-key"
    assert config.base_url is None

def test_get_llm_config_does_not_inherit_openai_key_for_local_provider(
    monkeypatch,
):
    monkeypatch.setenv("LLM_PROVIDER", "local")
    monkeypatch.setenv("LLM_MODEL", "local-model")
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    # Simulate an OpenAI key still being present in the environment.
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "legacy-openai-key",
    )

    config = get_llm_config()

    assert config.provider is LLMProviderType.LOCAL
    assert config.model == "local-model"
    assert config.api_key is None