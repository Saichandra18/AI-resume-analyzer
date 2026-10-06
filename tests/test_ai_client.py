import pytest

from app.ai.client import OpenAIClient


def test_client_requires_api_key(monkeypatch):
    monkeypatch.delenv(
        "OPENAI_API_KEY",
        raising=False,
    )

    with pytest.raises(ValueError):
        OpenAIClient()


def test_client_uses_environment_configuration(
    monkeypatch,
):
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "test-key",
    )
    monkeypatch.setenv(
        "OPENAI_MODEL",
        "test-model",
    )

    client = OpenAIClient()

    assert client.api_key == "test-key"
    assert client.model == "test-model"


def test_generate_rejects_empty_prompt(
    monkeypatch,
):
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "test-key",
    )

    client = OpenAIClient()

    with pytest.raises(ValueError):
        client.generate("")


def test_generate_rejects_whitespace_prompt(
    monkeypatch,
):
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "test-key",
    )

    client = OpenAIClient()

    with pytest.raises(ValueError):
        client.generate("   ")

def test_generate_returns_model_output(monkeypatch):
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "test-key",
    )

    client = OpenAIClient()

    class FakeResponse:
        output_text = "Rewritten response"

    class FakeResponses:
        def create(self, **kwargs):
            assert kwargs["model"] == client.model
            assert kwargs["input"] == (
                "Rewrite this professionally."
            )
            return FakeResponse()

    class FakeOpenAI:
        responses = FakeResponses()

    client.client = FakeOpenAI()

    result = client.generate(
        "Rewrite this professionally."
    )

    assert result == "Rewritten response"