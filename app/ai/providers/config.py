import os

from dotenv import load_dotenv

from .models import LLMConfig, LLMProviderType


load_dotenv()


def get_llm_config() -> LLMConfig:
    """
    Load the active LLM configuration from environment variables.

    Environment variables:
        LLM_PROVIDER: Provider type. Defaults to ``openai``.
        LLM_MODEL: Model name. Falls back to OPENAI_MODEL.
        LLM_API_KEY: Generic provider API key.
        LLM_BASE_URL: Optional provider base URL.

    Backward compatibility:
        OPENAI_API_KEY and OPENAI_MODEL remain supported so the
        existing OpenAI setup does not need to change yet.
    """

    provider_value = os.getenv("LLM_PROVIDER", "openai").strip().lower()

    try:
        provider = LLMProviderType(provider_value)
    except ValueError as exc:
        raise ValueError(
            f"Unsupported LLM provider: {provider_value}"
        ) from exc

    model = (
        os.getenv("LLM_MODEL")
        or os.getenv("OPENAI_MODEL")
        or ""
    ).strip()

    api_key = (
        os.getenv("LLM_API_KEY")
        or os.getenv("OPENAI_API_KEY")
    )

    base_url = os.getenv("LLM_BASE_URL")

    return LLMConfig(
        provider=provider,
        model=model,
        api_key=api_key,
        base_url=base_url,
    )