from .providers import (
    LLMProvider,
    LLMProviderType,
    OpenAIProvider,
    get_llm_config,
)


def create_llm_provider() -> LLMProvider:
    """
    Create the configured LLM provider.

    The application depends on the generic LLMProvider interface
    rather than directly selecting a vendor implementation.
    """

    config = get_llm_config()

    if config.provider is LLMProviderType.OPENAI:
        return OpenAIProvider(
            api_key=config.api_key,
            model=config.model,
        )

    raise ValueError(
        f"Unsupported LLM provider: {config.provider.value}"
    )