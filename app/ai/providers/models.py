from dataclasses import dataclass
from enum import Enum


class LLMProviderType(str, Enum):
    """Supported LLM provider types."""

    OPENAI = "openai"
    OPENAI_COMPATIBLE = "openai_compatible"
    LOCAL = "local"


@dataclass(frozen=True)
class LLMConfig:
    """
    Provider-neutral configuration for an LLM.

    The configuration describes how an LLM provider should be
    identified and accessed without implementing provider-specific
    behavior.
    """

    provider: LLMProviderType
    model: str
    api_key: str | None = None
    base_url: str | None = None

    def __post_init__(self):
        if not self.model or not self.model.strip():
            raise ValueError("Model must not be empty.")

        if not isinstance(self.provider, LLMProviderType):
            raise ValueError("Provider must be a valid LLMProviderType.")