import pytest

from app.ai.providers import LLMProvider
from app.ai.fallback import FallbackLLMProvider


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
        self.error = error or RuntimeError(
            "Provider request failed"
        )

    def generate(self, prompt: str) -> str:
        self.calls.append(prompt)
        raise self.error


def test_provider_error_is_available_as_common_exception():
    from app.ai.errors import ProviderError

    error = ProviderError("Provider unavailable")

    assert isinstance(error, Exception)
    assert str(error) == "Provider unavailable"


def test_provider_error_can_wrap_original_exception():
    from app.ai.errors import ProviderError

    original = RuntimeError("Connection refused")

    error = ProviderError(
        "Provider request failed"
    )

    error.__cause__ = original

    assert str(error) == "Provider request failed"
    assert error.__cause__ is original


def test_fallback_preserves_successful_primary_result():
    primary = SuccessfulProvider("primary")
    fallback = SuccessfulProvider("fallback")

    provider = FallbackLLMProvider(
        primary=primary,
        fallback=fallback,
    )

    result = provider.generate("Hello")

    assert result == "primary"
    assert primary.calls == ["Hello"]
    assert fallback.calls == []


def test_fallback_handles_provider_error():
    from app.ai.errors import ProviderError

    primary = FailingProvider(
        ProviderError("Primary unavailable")
    )
    fallback = SuccessfulProvider("fallback")

    provider = FallbackLLMProvider(
        primary=primary,
        fallback=fallback,
    )

    result = provider.generate("Hello")

    assert result == "fallback"
    assert primary.calls == ["Hello"]
    assert fallback.calls == ["Hello"]


def test_provider_error_is_propagated_without_fallback():
    from app.ai.errors import ProviderError

    error = ProviderError("Primary unavailable")
    primary = FailingProvider(error)

    provider = FallbackLLMProvider(
        primary=primary,
        fallback=None,
    )

    with pytest.raises(
        ProviderError,
        match="Primary unavailable",
    ):
        provider.generate("Hello")

    assert primary.calls == ["Hello"]


def test_fallback_error_is_propagated():
    from app.ai.errors import ProviderError

    primary = FailingProvider(
        ProviderError("Primary unavailable")
    )
    fallback = FailingProvider(
        ProviderError("Fallback unavailable")
    )

    provider = FallbackLLMProvider(
        primary=primary,
        fallback=fallback,
    )

    with pytest.raises(
        ProviderError,
        match="Fallback unavailable",
    ):
        provider.generate("Hello")


def test_provider_error_preserves_original_cause():
    from app.ai.errors import ProviderError

    original = RuntimeError("Connection refused")

    error = ProviderError(
        "Provider request failed"
    )

    error.__cause__ = original

    assert error.__cause__ is original


def test_fallback_does_not_retry_more_than_once():
    from app.ai.errors import ProviderError

    primary = FailingProvider(
        ProviderError("Primary unavailable")
    )
    fallback = SuccessfulProvider("fallback")

    provider = FallbackLLMProvider(
        primary=primary,
        fallback=fallback,
    )

    result = provider.generate("Hello")

    assert result == "fallback"
    assert len(primary.calls) == 1
    assert len(fallback.calls) == 1
