import pytest

from app.ai.providers import (
    LLMProvider,
    LocalProvider,
    OpenAICompatibleProvider,
    OpenAIProvider,
)


class FakeClient:
    def __init__(self):
        self.responses = self

    def create(self, **kwargs):
        class Response:
            output_text = "Generated response"

        return Response()


@pytest.mark.parametrize(
    "provider_class,kwargs",
    [
        (
            OpenAIProvider,
            {
                "api_key": "test-key",
                "model": "test-model",
            },
        ),
        (
            OpenAICompatibleProvider,
            {
                "api_key": "test-key",
                "model": "test-model",
                "base_url": "http://localhost:1234/v1",
            },
        ),
        (
            LocalProvider,
            {
                "model": "local-model",
                "base_url": "http://localhost:11434/v1",
            },
        ),
    ],
)
def test_all_providers_implement_common_interface(
    monkeypatch,
    provider_class,
    kwargs,
):
    provider = provider_class(**kwargs)

    assert isinstance(provider, LLMProvider)
    assert callable(provider.generate)


@pytest.mark.parametrize(
    "provider_class,kwargs",
    [
        (
            OpenAIProvider,
            {
                "api_key": "test-key",
                "model": "test-model",
            },
        ),
        (
            OpenAICompatibleProvider,
            {
                "api_key": "test-key",
                "model": "test-model",
                "base_url": "http://localhost:1234/v1",
            },
        ),
        (
            LocalProvider,
            {
                "model": "local-model",
                "base_url": "http://localhost:11434/v1",
            },
        ),
    ],
)
def test_provider_generate_contract_isolated_from_sdk(
    monkeypatch,
    provider_class,
    kwargs,
):
    provider = provider_class(**kwargs)

    provider.client = FakeClient()

    result = provider.generate("Hello")

    assert result == "Generated response"


@pytest.mark.parametrize(
    "provider_class,kwargs",
    [
        (
            OpenAIProvider,
            {
                "api_key": "test-key",
                "model": "test-model",
            },
        ),
        (
            OpenAICompatibleProvider,
            {
                "api_key": "test-key",
                "model": "test-model",
                "base_url": "http://localhost:1234/v1",
            },
        ),
        (
            LocalProvider,
            {
                "model": "local-model",
                "base_url": "http://localhost:11434/v1",
            },
        ),
    ],
)
def test_providers_use_same_generate_contract(
    provider_class,
    kwargs,
):
    provider = provider_class(**kwargs)

    assert hasattr(provider, "generate")
    assert callable(provider.generate)

    with pytest.raises(ValueError, match="Prompt must not be empty"):
        provider.generate("")


def test_provider_implementations_are_independently_substitutable():
    class StubProvider(LLMProvider):
        def generate(self, prompt: str) -> str:
            return "stub response"

    provider = StubProvider()

    assert isinstance(provider, LLMProvider)
    assert provider.generate("Hello") == "stub response"


def test_provider_isolation_does_not_require_vendor_selection_logic():
    class ProviderConsumer:
        def __init__(self, provider: LLMProvider):
            self.provider = provider

        def generate(self, prompt):
            return self.provider.generate(prompt)

    class StubProvider(LLMProvider):
        def generate(self, prompt: str) -> str:
            return f"generated: {prompt}"

    consumer = ProviderConsumer(StubProvider())

    assert consumer.generate("Hello") == "generated: Hello"