import pytest

from app.ai.providers import LLMProvider
from app.ai.providers.local import LocalProvider


class FakeResponse:
    output_text = "Generated local response"


class FakeResponses:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return FakeResponse()


class FakeOpenAIClient:
    def __init__(self, api_key=None, base_url=None):
        self.api_key = api_key
        self.base_url = base_url
        self.responses = FakeResponses()


def test_local_provider_implements_llm_provider(monkeypatch):
    monkeypatch.setattr(
        "app.ai.providers.local.OpenAI",
        FakeOpenAIClient,
    )

    provider = LocalProvider(
        model="local-model",
        base_url="http://localhost:11434/v1",
    )

    assert isinstance(provider, LLMProvider)


def test_local_provider_does_not_require_api_key(monkeypatch):
    monkeypatch.setattr(
        "app.ai.providers.local.OpenAI",
        FakeOpenAIClient,
    )

    provider = LocalProvider(
        model="local-model",
        base_url="http://localhost:11434/v1",
    )

    assert provider.api_key is None


@pytest.mark.parametrize("model", ["", "   ", None])
def test_local_provider_requires_model(monkeypatch, model):
    monkeypatch.setattr(
        "app.ai.providers.local.OpenAI",
        FakeOpenAIClient,
    )

    with pytest.raises(
        ValueError,
        match="Model must not be empty",
    ):
        LocalProvider(
            model=model,
            base_url="http://localhost:11434/v1",
        )


@pytest.mark.parametrize("base_url", ["", "   ", None])
def test_local_provider_requires_base_url(monkeypatch, base_url):
    monkeypatch.setattr(
        "app.ai.providers.local.OpenAI",
        FakeOpenAIClient,
    )

    with pytest.raises(
        ValueError,
        match="Base URL must not be empty",
    ):
        LocalProvider(
            model="local-model",
            base_url=base_url,
        )


def test_local_provider_initializes_client_with_base_url(
    monkeypatch,
):
    clients = []

    def fake_openai(**kwargs):
        client = FakeOpenAIClient(**kwargs)
        clients.append(client)
        return client

    monkeypatch.setattr(
        "app.ai.providers.local.OpenAI",
        fake_openai,
    )

    provider = LocalProvider(
        model="local-model",
        base_url="http://localhost:11434/v1",
    )

    assert provider.model == "local-model"
    assert provider.base_url == "http://localhost:11434/v1"
    assert len(clients) == 1

    # The provider keeps its configured API key unset, but passes
    # a local placeholder to the SDK.
    assert provider.api_key is None
    assert clients[0].api_key == "local"
    assert clients[0].base_url == "http://localhost:11434/v1"


def test_local_provider_does_not_modify_openai_api_key(
    monkeypatch,
):
    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "existing-openai-key",
    )

    monkeypatch.setattr(
        "app.ai.providers.local.OpenAI",
        FakeOpenAIClient,
    )

    LocalProvider(
        model="local-model",
        base_url="http://localhost:11434/v1",
    )

    assert (
        __import__("os").environ.get("OPENAI_API_KEY")
        == "existing-openai-key"
    )


def test_local_provider_does_not_add_openai_api_key(
    monkeypatch,
):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    monkeypatch.setattr(
        "app.ai.providers.local.OpenAI",
        FakeOpenAIClient,
    )

    LocalProvider(
        model="local-model",
        base_url="http://localhost:11434/v1",
    )

    assert "OPENAI_API_KEY" not in __import__("os").environ


def test_generate_rejects_empty_prompt(monkeypatch):
    monkeypatch.setattr(
        "app.ai.providers.local.OpenAI",
        FakeOpenAIClient,
    )

    provider = LocalProvider(
        model="local-model",
        base_url="http://localhost:11434/v1",
    )

    with pytest.raises(
        ValueError,
        match="Prompt must not be empty",
    ):
        provider.generate("")


@pytest.mark.parametrize("prompt", ["", "   ", None])
def test_generate_rejects_invalid_prompt(monkeypatch, prompt):
    monkeypatch.setattr(
        "app.ai.providers.local.OpenAI",
        FakeOpenAIClient,
    )

    provider = LocalProvider(
        model="local-model",
        base_url="http://localhost:11434/v1",
    )

    with pytest.raises(
        ValueError,
        match="Prompt must not be empty",
    ):
        provider.generate(prompt)


def test_generate_uses_configured_model_and_prompt(monkeypatch):
    client = FakeOpenAIClient(
        api_key="local",
        base_url="http://localhost:11434/v1",
    )

    monkeypatch.setattr(
        "app.ai.providers.local.OpenAI",
        lambda **kwargs: client,
    )

    provider = LocalProvider(
        model="local-model",
        base_url="http://localhost:11434/v1",
    )

    result = provider.generate(
        "Create a concise resume summary."
    )

    assert result == "Generated local response"
    assert client.responses.calls == [
        {
            "model": "local-model",
            "input": "Create a concise resume summary.",
        }
    ]


def test_generate_returns_response_output_text(monkeypatch):
    monkeypatch.setattr(
        "app.ai.providers.local.OpenAI",
        FakeOpenAIClient,
    )

    provider = LocalProvider(
        model="local-model",
        base_url="http://localhost:11434/v1",
    )

    assert provider.generate("Hello") == "Generated local response"


def test_local_provider_does_not_require_real_network(monkeypatch):
    monkeypatch.setattr(
        "app.ai.providers.local.OpenAI",
        FakeOpenAIClient,
    )

    provider = LocalProvider(
        model="local-model",
        base_url="http://localhost:11434/v1",
    )

    assert provider.generate("Test") == "Generated local response"


def test_provider_does_not_swallow_provider_errors(monkeypatch):
    class FailingResponses:
        def create(self, **kwargs):
            raise RuntimeError("Local provider request failed")

    class FailingClient:
        def __init__(self, **kwargs):
            self.responses = FailingResponses()

    monkeypatch.setattr(
        "app.ai.providers.local.OpenAI",
        FailingClient,
    )

    provider = LocalProvider(
        model="local-model",
        base_url="http://localhost:11434/v1",
    )

    with pytest.raises(
        RuntimeError,
        match="Local provider request failed",
    ):
        provider.generate("Hello")
