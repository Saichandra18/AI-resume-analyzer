import pytest

from app.ai.factory import create_llm_provider
from app.ai.providers import LLMProvider, OpenAIProvider


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


@pytest.mark.parametrize(
    "provider_name",
    [
        "openai_compatible",
        "local",
    ],
)
def test_factory_rejects_unimplemented_providers(
    monkeypatch,
    provider_name,
):
    monkeypatch.setenv("LLM_PROVIDER", provider_name)
    monkeypatch.setenv("LLM_MODEL", "test-model")

    with pytest.raises(
        ValueError,
        match=f"Unsupported LLM provider: {provider_name}",
    ):
        create_llm_provider()