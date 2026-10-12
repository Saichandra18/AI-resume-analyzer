import pytest
import os
from app.ai.providers import LLMProvider


def test_anthropic_provider_implements_llm_provider():
    from app.ai.providers.anthropic import AnthropicProvider

    provider = AnthropicProvider(
        api_key="test-key",
        model="claude-test",
    )

    assert isinstance(provider, LLMProvider)


def test_anthropic_provider_requires_api_key():
    from app.ai.providers.anthropic import AnthropicProvider

    with pytest.raises(
        ValueError,
        match="API key is not configured",
    ):
        AnthropicProvider(
            api_key=None,
            model="claude-test",
        )


def test_anthropic_provider_rejects_empty_api_key():
    from app.ai.providers.anthropic import AnthropicProvider

    with pytest.raises(
        ValueError,
        match="API key is not configured",
    ):
        AnthropicProvider(
            api_key="",
            model="claude-test",
        )


def test_anthropic_provider_requires_model():
    from app.ai.providers.anthropic import AnthropicProvider

    with pytest.raises(
        ValueError,
        match="Model must not be empty",
    ):
        AnthropicProvider(
            api_key="test-key",
            model=None,
        )


def test_anthropic_provider_rejects_empty_model():
    from app.ai.providers.anthropic import AnthropicProvider

    with pytest.raises(
        ValueError,
        match="Model must not be empty",
    ):
        AnthropicProvider(
            api_key="test-key",
            model="",
        )


def test_anthropic_provider_stores_configuration():
    from app.ai.providers.anthropic import AnthropicProvider

    provider = AnthropicProvider(
        api_key="test-key",
        model="claude-test",
    )

    assert provider.api_key == "test-key"
    assert provider.model == "claude-test"


def test_anthropic_provider_rejects_empty_prompt():
    from app.ai.providers.anthropic import AnthropicProvider

    provider = AnthropicProvider(
        api_key="test-key",
        model="claude-test",
    )

    with pytest.raises(
        ValueError,
        match="Prompt must not be empty",
    ):
        provider.generate("")


def test_anthropic_provider_rejects_whitespace_prompt():
    from app.ai.providers.anthropic import AnthropicProvider

    provider = AnthropicProvider(
        api_key="test-key",
        model="claude-test",
    )

    with pytest.raises(
        ValueError,
        match="Prompt must not be empty",
    ):
        provider.generate("   ")


def test_anthropic_provider_uses_anthropic_client(monkeypatch):
    from app.ai.providers import anthropic

    captured = {}

    class FakeMessages:
        def create(self, **kwargs):
            captured.update(kwargs)

            class Response:
                content = [
                    type(
                        "Content",
                        (),
                        {"text": "generated response"},
                    )()
                ]

            return Response()

    class FakeAnthropic:
        def __init__(self, api_key):
            captured["api_key"] = api_key
            self.messages = FakeMessages()

    monkeypatch.setattr(
        anthropic,
        "Anthropic",
        FakeAnthropic,
    )

    provider = anthropic.AnthropicProvider(
        api_key="test-key",
        model="claude-test",
    )

    result = provider.generate("Hello")

    assert result == "generated response"
    assert captured["api_key"] == "test-key"
    assert captured["model"] == "claude-test"
    assert captured["messages"] == [
        {
            "role": "user",
            "content": "Hello",
        }
    ]


def test_anthropic_provider_sends_max_tokens():
    from app.ai.providers import anthropic

    captured = {}

    class FakeMessages:
        def create(self, **kwargs):
            captured.update(kwargs)

            class Response:
                content = [
                    type(
                        "Content",
                        (),
                        {"text": "response"},
                    )()
                ]

            return Response()

    class FakeAnthropic:
        def __init__(self, api_key):
            self.messages = FakeMessages()

    monkeypatch = pytest.MonkeyPatch()

    try:
        monkeypatch.setattr(
            anthropic,
            "Anthropic",
            FakeAnthropic,
        )

        provider = anthropic.AnthropicProvider(
            api_key="test-key",
            model="claude-test",
        )

        provider.generate("Hello")

        assert captured["max_tokens"] == 4096
    finally:
        monkeypatch.undo()


def test_anthropic_provider_propagates_client_errors():
    from app.ai.providers import anthropic

    class FakeMessages:
        def create(self, **kwargs):
            raise RuntimeError("Anthropic request failed")

    class FakeAnthropic:
        def __init__(self, api_key):
            self.messages = FakeMessages()

    monkeypatch = pytest.MonkeyPatch()

    try:
        monkeypatch.setattr(
            anthropic,
            "Anthropic",
            FakeAnthropic,
        )

        provider = anthropic.AnthropicProvider(
            api_key="test-key",
            model="claude-test",
        )

        with pytest.raises(
            RuntimeError,
            match="Anthropic request failed",
        ):
            provider.generate("Hello")
    finally:
        monkeypatch.undo()


def test_anthropic_provider_does_not_modify_openai_environment(
    monkeypatch,
):
    from app.ai.providers import anthropic

    monkeypatch.setenv(
        "OPENAI_API_KEY",
        "existing-openai-key",
    )

    class FakeAnthropic:
        def __init__(self, api_key):
            pass

    monkeypatch.setattr(
        anthropic,
        "Anthropic",
        FakeAnthropic,
    )

    anthropic.AnthropicProvider(
        api_key="anthropic-key",
        model="claude-test",
    )

    assert (
        os.environ.get("OPENAI_API_KEY")
        == "existing-openai-key"
    )
