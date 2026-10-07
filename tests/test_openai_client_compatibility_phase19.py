from unittest.mock import Mock

import pytest

from app.ai.client import OpenAIClient
from app.ai.providers import OpenAIProvider


def test_openai_client_uses_openai_provider(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    client = OpenAIClient(model="test-model")

    assert isinstance(client.provider, OpenAIProvider)
    assert client.model == "test-model"
    assert client.api_key == "test-key"


def test_openai_client_preserves_generate_behavior(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    client = OpenAIClient(model="test-model")

    client.provider.generate = Mock(
        return_value="Generated response"
    )

    result = client.generate("Hello")

    client.provider.generate.assert_called_once_with("Hello")
    assert result == "Generated response"


def test_openai_client_exposes_underlying_client(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    client = OpenAIClient()

    assert client.client is client.provider.client


def test_openai_client_rejects_empty_prompt(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    client = OpenAIClient()

    with pytest.raises(
        ValueError,
        match="Prompt must not be empty",
    ):
        client.generate("")