from .providers import (
    LLMProvider,
    LocalProvider,
    OpenAICompatibleProvider,
    OpenAIProvider,
    get_llm_config,
)
from .providers.anthropic import AnthropicProvider
from .providers.models import LLMProviderType
from .registry import LLMProviderRegistry


def _build_provider_registry() -> LLMProviderRegistry:
    """Build the registry containing the built-in providers."""

    registry = LLMProviderRegistry()

    registry.register_factory(
        "openai",
        OpenAIProvider,
        lambda **kwargs: OpenAIProvider(
            api_key=kwargs.get("api_key"),
            model=kwargs.get("model"),
        ),
    )

    registry.register_factory(
        "openai_compatible",
        OpenAICompatibleProvider,
        lambda **kwargs: OpenAICompatibleProvider(
            api_key=kwargs.get("api_key"),
            model=kwargs.get("model"),
            base_url=kwargs.get("base_url"),
        ),
    )

    registry.register_factory(
        "local",
        LocalProvider,
        lambda **kwargs: LocalProvider(
            api_key=kwargs.get("api_key"),
            model=kwargs.get("model"),
            base_url=kwargs.get("base_url"),
        ),
    )

    registry.register_factory(
        "anthropic",
        AnthropicProvider,
        lambda **kwargs: AnthropicProvider(
            api_key=kwargs.get("api_key"),
            model=kwargs.get("model"),
        ),
    )

    return registry


# One shared registry for the application.
_PROVIDER_REGISTRY = _build_provider_registry()


def get_provider_registry() -> LLMProviderRegistry:
    """Return the shared registry so additional providers can be registered."""
    return _PROVIDER_REGISTRY


def create_llm_provider() -> LLMProvider:
    """Create the provider selected by the current LLM configuration."""

    config = get_llm_config()

    provider_name = (
        config.provider.value
        if isinstance(config.provider, LLMProviderType)
        else config.provider
    )

    if _PROVIDER_REGISTRY.get(provider_name) is None:
        raise ValueError(
            f"Unsupported LLM provider: {provider_name}"
        )

    return _PROVIDER_REGISTRY.create(
        provider_name,
        api_key=config.api_key,
        model=config.model,
        base_url=config.base_url,
    )
