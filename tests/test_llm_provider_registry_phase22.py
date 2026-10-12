import pytest

from app.ai.providers import LLMProvider
from app.ai.registry import LLMProviderRegistry


class FakeProvider(LLMProvider):
    def __init__(self, result="generated"):
        self.result = result
        self.calls = []

    def generate(self, prompt: str) -> str:
        self.calls.append(prompt)
        return self.result


class AnotherFakeProvider(LLMProvider):
    def generate(self, prompt: str) -> str:
        return "another-result"


def test_registry_can_register_provider():
    registry = LLMProviderRegistry()

    registry.register("fake", FakeProvider)

    assert registry.get("fake") is FakeProvider


def test_registry_can_register_multiple_providers():
    registry = LLMProviderRegistry()

    registry.register("fake", FakeProvider)
    registry.register(
        "another",
        AnotherFakeProvider,
    )

    assert registry.get("fake") is FakeProvider
    assert registry.get("another") is AnotherFakeProvider


def test_registry_rejects_non_provider_class():
    registry = LLMProviderRegistry()

    class InvalidProvider:
        pass

    with pytest.raises(
        TypeError,
        match="must implement LLMProvider",
    ):
        registry.register(
            "invalid",
            InvalidProvider,
        )


def test_registry_rejects_empty_provider_name():
    registry = LLMProviderRegistry()

    with pytest.raises(
        ValueError,
        match="Provider name must not be empty",
    ):
        registry.register(
            "",
            FakeProvider,
        )


def test_registry_rejects_whitespace_provider_name():
    registry = LLMProviderRegistry()

    with pytest.raises(
        ValueError,
        match="Provider name must not be empty",
    ):
        registry.register(
            "   ",
            FakeProvider,
        )


def test_registry_rejects_duplicate_provider():
    registry = LLMProviderRegistry()

    registry.register("fake", FakeProvider)

    with pytest.raises(
        ValueError,
        match="already registered",
    ):
        registry.register(
            "fake",
            AnotherFakeProvider,
        )


def test_registry_returns_none_for_unknown_provider():
    registry = LLMProviderRegistry()

    assert registry.get("unknown") is None


def test_registry_can_list_registered_providers():
    registry = LLMProviderRegistry()

    registry.register("fake", FakeProvider)
    registry.register(
        "another",
        AnotherFakeProvider,
    )

    providers = registry.list_providers()

    assert providers == [
        "fake",
        "another",
    ]


def test_registry_provider_can_be_instantiated():
    registry = LLMProviderRegistry()

    registry.register("fake", FakeProvider)

    provider_class = registry.get("fake")

    provider = provider_class(
        result="test-result",
    )

    assert isinstance(provider, LLMProvider)
    assert provider.generate("Hello") == "test-result"


def test_registry_names_are_normalized():
    registry = LLMProviderRegistry()

    registry.register(
        "  FakeProvider  ",
        FakeProvider,
    )

    assert registry.get("fakeprovider") is FakeProvider


def test_registry_is_case_insensitive():
    registry = LLMProviderRegistry()

    registry.register(
        "Anthropic",
        FakeProvider,
    )

    assert registry.get("anthropic") is FakeProvider
    assert registry.get("ANTHROPIC") is FakeProvider


def test_registry_does_not_require_vendor_specific_logic():
    registry = LLMProviderRegistry()

    registry.register("provider-a", FakeProvider)
    registry.register(
        "provider-b",
        AnotherFakeProvider,
    )

    assert registry.get("provider-a") is FakeProvider
    assert registry.get("provider-b") is AnotherFakeProvider


def test_registered_provider_must_be_subclass_of_llm_provider():
    registry = LLMProviderRegistry()

    class InvalidProvider:
        def generate(self, prompt):
            return "invalid"

    with pytest.raises(
        TypeError,
        match="must implement LLMProvider",
    ):
        registry.register(
            "invalid",
            InvalidProvider,
        )
