import os
from dataclasses import dataclass

from dotenv import load_dotenv

from .models import LLMConfig, LLMProviderType


load_dotenv()


@dataclass(frozen=True)
class _RuntimeLLMConfig:
    """Runtime configuration for a registered custom provider."""

    provider: str
    model: str
    api_key: str | None = None
    base_url: str | None = None

    def __post_init__(self):
        if not isinstance(self.model, str) or not self.model.strip():
            raise ValueError("Model must not be empty.")

        if not isinstance(self.provider, str) or not self.provider.strip():
            raise ValueError("Provider must not be empty.")


def get_llm_config() -> LLMConfig | _RuntimeLLMConfig:
    """Load configuration for a built-in or registered custom provider."""

    provider_value = (
        os.getenv("LLM_PROVIDER", "openai").strip().lower()
    )

    try:
        provider = LLMProviderType(provider_value)
    except ValueError:
        # Import lazily to avoid a circular import during module loading.
        from app.ai.factory import get_provider_registry

        registry = get_provider_registry()

        if registry.get(provider_value) is None:
            raise ValueError(
                f"Unsupported LLM provider: {provider_value}"
            )

        provider = provider_value

    model = (
        os.getenv("LLM_MODEL")
        or os.getenv("OPENAI_MODEL")
        or ""
    ).strip()

    if os.getenv("LLM_API_KEY"):
        api_key = os.getenv("LLM_API_KEY")
    elif provider == LLMProviderType.OPENAI:
        api_key = os.getenv("OPENAI_API_KEY")
    else:
        api_key = None

    base_url = os.getenv("LLM_BASE_URL")

    config_class = (
        _RuntimeLLMConfig
        if isinstance(provider, str)
        and not isinstance(provider, LLMProviderType)
        else LLMConfig
    )

    return config_class(
        provider=provider,
        model=model,
        api_key=api_key,
        base_url=base_url,
    )