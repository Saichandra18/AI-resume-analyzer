import pytest

from app.ai.providers import LLMProvider


class SuccessfulProvider(LLMProvider):
    def __init__(self, result="success"):
        self.result = result
        self.calls = []

    def generate(self, prompt: str) -> str:
        self.calls.append(prompt)
        return self.result


class FailingProvider(LLMProvider):
    def __init__(self, error=None):
        self.calls = []
        self.error = error or RuntimeError("Primary provider failed")

    def generate(self, prompt: str) -> str:
        self.calls.append(prompt)
        raise self.error


def test_primary_provider_is_used_when_successful():
    primary = SuccessfulProvider("primary result")
    fallback = SuccessfulProvider("fallback result")

    # Fallback orchestration will be implemented in the next step.
    from app.ai.fallback import FallbackLLMProvider

    provider = FallbackLLMProvider(
        primary=primary,
        fallback=fallback,
    )

    result = provider.generate("Hello")

    assert result == "primary result"
    assert primary.calls == ["Hello"]
    assert fallback.calls == []


def test_fallback_is_used_when_primary_fails():
    primary = FailingProvider()
    fallback = SuccessfulProvider("fallback result")

    from app.ai.fallback import FallbackLLMProvider

    provider = FallbackLLMProvider(
        primary=primary,
        fallback=fallback,
    )

    result = provider.generate("Hello")

    assert result == "fallback result"
    assert primary.calls == ["Hello"]
    assert fallback.calls == ["Hello"]


def test_primary_error_is_raised_when_fallback_is_disabled():
    primary = FailingProvider()

    from app.ai.fallback import FallbackLLMProvider

    provider = FallbackLLMProvider(
        primary=primary,
        fallback=None,
    )

    with pytest.raises(
        RuntimeError,
        match="Primary provider failed",
    ):
        provider.generate("Hello")

    assert primary.calls == ["Hello"]


def test_fallback_error_is_propagated():
    primary = FailingProvider(
        RuntimeError("Primary failed"),
    )
    fallback = FailingProvider(
        RuntimeError("Fallback failed"),
    )

    from app.ai.fallback import FallbackLLMProvider

    provider = FallbackLLMProvider(
        primary=primary,
        fallback=fallback,
    )

    with pytest.raises(
        RuntimeError,
        match="Fallback failed",
    ):
        provider.generate("Hello")


def test_fallback_does_not_retry_multiple_times():
    primary = FailingProvider()
    fallback = SuccessfulProvider("fallback")

    from app.ai.fallback import FallbackLLMProvider

    provider = FallbackLLMProvider(
        primary=primary,
        fallback=fallback,
    )

    provider.generate("Hello")

    assert len(primary.calls) == 1
    assert len(fallback.calls) == 1


def test_fallback_provider_receives_same_prompt():
    primary = FailingProvider()
    fallback = SuccessfulProvider("fallback")

    from app.ai.fallback import FallbackLLMProvider

    provider = FallbackLLMProvider(
        primary=primary,
        fallback=fallback,
    )

    provider.generate(
        "Create a JD-optimized resume summary."
    )

    assert primary.calls == [
        "Create a JD-optimized resume summary."
    ]
    assert fallback.calls == [
        "Create a JD-optimized resume summary."
    ]


def test_fallback_provider_implements_llm_provider():
    primary = SuccessfulProvider()
    fallback = SuccessfulProvider()

    from app.ai.fallback import FallbackLLMProvider

    provider = FallbackLLMProvider(
        primary=primary,
        fallback=fallback,
    )

    assert isinstance(provider, LLMProvider)