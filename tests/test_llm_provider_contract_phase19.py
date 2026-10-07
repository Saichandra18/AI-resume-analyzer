import pytest

from app.ai.providers import LLMProvider


class FakeProvider(LLMProvider):
    """Simple provider used to verify the common provider contract."""

    def generate(self, prompt: str) -> str:
        if not prompt or not str(prompt).strip():
            raise ValueError("Prompt must not be empty.")

        return f"generated: {prompt}"


@pytest.fixture
def provider():
    return FakeProvider()


def test_provider_is_an_llm_provider(provider):
    assert isinstance(provider, LLMProvider)


def test_provider_generate_returns_text(provider):
    result = provider.generate("Hello")

    assert isinstance(result, str)
    assert result == "generated: Hello"


def test_provider_generate_accepts_normal_prompt(provider):
    assert provider.generate("Build an AI resume analyzer.") == (
        "generated: Build an AI resume analyzer."
    )


@pytest.mark.parametrize(
    "prompt",
    [
        "",
        "   ",
        "\t",
        "\n",
    ],
)
def test_provider_rejects_empty_prompt(provider, prompt):
    with pytest.raises(ValueError, match="Prompt must not be empty"):
        provider.generate(prompt)


def test_provider_can_be_substituted_without_vendor_knowledge():
    def generate_resume_text(provider: LLMProvider, prompt: str) -> str:
        return provider.generate(prompt)

    provider = FakeProvider()

    result = generate_resume_text(
        provider,
        "Create a professional summary.",
    )

    assert result == "generated: Create a professional summary."


def test_provider_contract_requires_generate():
    class InvalidProvider(LLMProvider):
        pass

    with pytest.raises(TypeError):
        InvalidProvider()


def test_provider_contract_supports_multiple_implementations():
    class ProviderA(LLMProvider):
        def generate(self, prompt: str) -> str:
            return f"A: {prompt}"

    class ProviderB(LLMProvider):
        def generate(self, prompt: str) -> str:
            return f"B: {prompt}"

    providers = [
        ProviderA(),
        ProviderB(),
    ]

    results = [
        provider.generate("test")
        for provider in providers
    ]

    assert results == [
        "A: test",
        "B: test",
    ]