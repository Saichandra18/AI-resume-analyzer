from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """
    Abstract interface for all LLM providers.

    Application services depend on this interface rather than
    depending directly on a specific LLM vendor.
    """

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate text from a prompt.

        Args:
            prompt: Input prompt sent to the language model.

        Returns:
            Generated text.

        Raises:
            ValueError: If the prompt is invalid.
            Exception: Provider-specific failures may propagate.
        """
        raise NotImplementedError