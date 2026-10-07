import pytest

from app.ai.providers import OpenAIProvider, LLMProvider


def test_openai_provider_implements_llm_provider(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    provider = OpenAIProvider(model="test-model")

    assert isinstance(provider, LLMProvider)
    assert provider.model == "test-model"
    assert provider.api_key == "test-key"


def test_openai_provider_uses_environment_configuration(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "environment-key")
    monkeypatch.setenv("OPENAI_MODEL", "environment-model")

    provider = OpenAIProvider()

    assert provider.api_key == "environment-key"
    assert provider.model == "environment-model"


def test_openai_provider_rejects_missing_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(
        ValueError,
        match="OPENAI_API_KEY is not configured",
    ):
        OpenAIProvider()


def test_openai_provider_rejects_empty_prompt(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    provider = OpenAIProvider()

    with pytest.raises(
        ValueError,
        match="Prompt must not be empty",
    ):
        provider.generate("")


def test_openai_provider_rejects_whitespace_prompt(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    provider = OpenAIProvider()

    with pytest.raises(
        ValueError,
        match="Prompt must not be empty",
    ):
        provider.generate("   ")


def test_openai_provider_generate_uses_responses_api(
    monkeypatch,
):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    provider = OpenAIProvider(model="test-model")

    class FakeResponse:
        output_text = "Generated response"

    calls = {}

    def fake_create(**kwargs):
        calls.update(kwargs)
        return FakeResponse()

    provider.client.responses.create = fake_create

    result = provider.generate("Hello")

    assert result == "Generated response"
    assert calls == {
        "model": "test-model",
        "input": "Hello",
    }