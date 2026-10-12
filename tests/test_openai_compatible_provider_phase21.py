import pytest

from app.ai.providers import LLMProvider
from app.ai.providers.openai_compatible import OpenAICompatibleProvider


class FakeResponse:
    output_text = "Generated compatible response"


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


def test_openai_compatible_provider_implements_llm_provider(
    monkeypatch,
):
    monkeypatch.setattr(
        "app.ai.providers.openai_compatible.OpenAI",
        FakeOpenAIClient,
    )

    provider = OpenAICompatibleProvider(
        api_key="test-key",
        model="test-model",
        base_url="http://localhost:1234/v1",
    )

    assert isinstance(provider, LLMProvider)


def test_provider_requires_api_key(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(
        ValueError,
        match="API key is not configured",
    ):
        OpenAICompatibleProvider(
            api_key=None,
            model="test-model",
            base_url="http://localhost:1234/v1",
        )


@pytest.mark.parametrize(
    "model",
    [
        "",
        "   ",
        None,
    ],
)
def test_provider_requires_model(
    monkeypatch,
    model,
):
    monkeypatch.setattr(
        "app.ai.providers.openai_compatible.OpenAI",
        FakeOpenAIClient,
    )

    with pytest.raises(
        ValueError,
        match="Model must not be empty",
    ):
        OpenAICompatibleProvider(
            api_key="test-key",
            model=model,
            base_url="http://localhost:1234/v1",
        )


@pytest.mark.parametrize(
    "base_url",
    [
        "",
        "   ",
        None,
    ],
)
def test_provider_requires_base_url(
    monkeypatch,
    base_url,
):
    monkeypatch.setattr(
        "app.ai.providers.openai_compatible.OpenAI",
        FakeOpenAIClient,
    )

    with pytest.raises(
        ValueError,
        match="Base URL must not be empty",
    ):
        OpenAICompatibleProvider(
            api_key="test-key",
            model="test-model",
            base_url=base_url,
        )


def test_provider_initializes_client_with_api_key_and_base_url(
    monkeypatch,
):
    clients = []

    def fake_openai(**kwargs):
        client = FakeOpenAIClient(**kwargs)
        clients.append(client)
        return client

    monkeypatch.setattr(
        "app.ai.providers.openai_compatible.OpenAI",
        fake_openai,
    )

    provider = OpenAICompatibleProvider(
        api_key="test-key",
        model="test-model",
        base_url="http://localhost:1234/v1",
    )

    assert provider.api_key == "test-key"
    assert provider.model == "test-model"
    assert provider.base_url == "http://localhost:1234/v1"

    assert len(clients) == 1
    assert clients[0].api_key == "test-key"
    assert clients[0].base_url == "http://localhost:1234/v1"


def test_generate_rejects_empty_prompt(
    monkeypatch,
):
    monkeypatch.setattr(
        "app.ai.providers.openai_compatible.OpenAI",
        FakeOpenAIClient,
    )

    provider = OpenAICompatibleProvider(
        api_key="test-key",
        model="test-model",
        base_url="http://localhost:1234/v1",
    )

    with pytest.raises(
        ValueError,
        match="Prompt must not be empty",
    ):
        provider.generate("")


@pytest.mark.parametrize(
    "prompt",
    [
        "",
        "   ",
        None,
    ],
)
def test_generate_rejects_invalid_prompt(
    monkeypatch,
    prompt,
):
    monkeypatch.setattr(
        "app.ai.providers.openai_compatible.OpenAI",
        FakeOpenAIClient,
    )

    provider = OpenAICompatibleProvider(
        api_key="test-key",
        model="test-model",
        base_url="http://localhost:1234/v1",
    )

    with pytest.raises(
        ValueError,
        match="Prompt must not be empty",
    ):
        provider.generate(prompt)


def test_generate_uses_configured_model_and_prompt(
    monkeypatch,
):
    client = FakeOpenAIClient(
        api_key="test-key",
        base_url="http://localhost:1234/v1",
    )

    monkeypatch.setattr(
        "app.ai.providers.openai_compatible.OpenAI",
        lambda **kwargs: client,
    )

    provider = OpenAICompatibleProvider(
        api_key="test-key",
        model="compatible-model",
        base_url="http://localhost:1234/v1",
    )

    result = provider.generate("Write a resume summary.")

    assert result == "Generated compatible response"

    assert client.responses.calls == [
        {
            "model": "compatible-model",
            "input": "Write a resume summary.",
        }
    ]


def test_generate_returns_response_output_text(
    monkeypatch,
):
    monkeypatch.setattr(
        "app.ai.providers.openai_compatible.OpenAI",
        FakeOpenAIClient,
    )

    provider = OpenAICompatibleProvider(
        api_key="test-key",
        model="test-model",
        base_url="http://localhost:1234/v1",
    )

    assert provider.generate("Hello") == (
        "Generated compatible response"
    )


def test_provider_does_not_swallow_provider_errors(
    monkeypatch,
):
    class FailingResponses:
        def create(self, **kwargs):
            raise RuntimeError("Provider request failed")

    class FailingClient:
        def __init__(self, **kwargs):
            self.responses = FailingResponses()

    monkeypatch.setattr(
        "app.ai.providers.openai_compatible.OpenAI",
        FailingClient,
    )

    provider = OpenAICompatibleProvider(
        api_key="test-key",
        model="test-model",
        base_url="http://localhost:1234/v1",
    )

    with pytest.raises(
        RuntimeError,
        match="Provider request failed",
    ):
        provider.generate("Hello")