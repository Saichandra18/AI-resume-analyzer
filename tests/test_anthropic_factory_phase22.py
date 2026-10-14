import pytest

from app.ai.providers import LLMProvider


def test_factory_creates_anthropic_provider(monkeypatch):
    from app.ai.factory import create_llm_provider

    monkeypatch.setenv(
        "LLM_PROVIDER",
        "anthropic",
    )
    monkeypatch.setenv(
        "LLM_MODEL",
        "claude-test",
    )
    monkeypatch.setenv(
        "LLM_API_KEY",
        "anthropic-test-key",
    )
    monkeypatch.delenv(
        "LLM_BASE_URL",
        raising=False,
    )

    provider = create_llm_provider()

    from app.ai.providers.anthropic import AnthropicProvider

    assert isinstance(provider, AnthropicProvider)
    assert isinstance(provider, LLMProvider)
    assert provider.model == "claude-test"
    assert provider.api_key == "anthropic-test-key"


def test_factory_anthropic_provider_uses_registry(
    monkeypatch,
):
    from app.ai.factory import create_llm_provider

    monkeypatch.setenv(
        "LLM_PROVIDER",
        "anthropic",
    )
    monkeypatch.setenv(
        "LLM_MODEL",
        "claude-test",
    )
    monkeypatch.setenv(
        "LLM_API_KEY",
        "anthropic-test-key",
    )

    provider = create_llm_provider()

    assert provider.__class__.__name__ == "AnthropicProvider"


def test_factory_still_rejects_unknown_provider(
    monkeypatch,
):
    from app.ai.factory import create_llm_provider

    monkeypatch.setenv(
        "LLM_PROVIDER",
        "totally-unknown",
    )
    monkeypatch.setenv(
        "LLM_MODEL",
        "test-model",
    )

    with pytest.raises(
        ValueError,
        match="Unsupported LLM provider: totally-unknown",
    ):
        create_llm_provider()