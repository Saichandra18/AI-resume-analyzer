import pytest

from app.ai.providers import LLMProvider


def test_llm_provider_is_abstract():
    with pytest.raises(TypeError):
        LLMProvider()


def test_llm_provider_requires_generate():
    class IncompleteProvider(LLMProvider):
        pass

    with pytest.raises(TypeError):
        IncompleteProvider()


def test_llm_provider_can_be_implemented():
    class FakeProvider(LLMProvider):
        def generate(self, prompt: str) -> str:
            return f"generated: {prompt}"

    provider = FakeProvider()

    assert provider.generate("Hello") == "generated: Hello"


def test_llm_provider_generate_accepts_prompt():
    class FakeProvider(LLMProvider):
        def generate(self, prompt: str) -> str:
            return prompt.upper()

    provider = FakeProvider()

    assert provider.generate("hello") == "HELLO"