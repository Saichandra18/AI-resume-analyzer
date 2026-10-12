from dataclasses import dataclass
from enum import Enum


class LLMProviderType(str, Enum):
    OPENAI = "openai"
    OPENAI_COMPATIBLE = "openai_compatible"
    LOCAL = "local"
    ANTHROPIC = "anthropic"


@dataclass(frozen=True)
class LLMConfig:
    """
    Provider-neutral configuration for an LLM.

    Built-in provider configurations use LLMProviderType.
    """

    provider: LLMProviderType
    model: str
    api_key: str | None = None
    base_url: str | None = None

    def __post_init__(self):
        if not isinstance(self.model, str) or not self.model.strip():
            raise ValueError("Model must not be empty.")

        if not isinstance(self.provider, LLMProviderType):
            raise ValueError(
                "Provider must be a valid LLMProviderType."
            )