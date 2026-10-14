from .providers import LLMProvider


class FallbackLLMProvider(LLMProvider):
    """
    Wrap a primary LLM provider with an optional fallback provider.

    The primary provider is always attempted first. The fallback is
    used only when the primary provider raises an exception.
    """

    def __init__(
        self,
        primary: LLMProvider,
        fallback: LLMProvider | None = None,
    ):
        if not isinstance(primary, LLMProvider):
            raise TypeError(
                "Primary provider must implement LLMProvider."
            )

        if fallback is not None and not isinstance(
            fallback,
            LLMProvider,
        ):
            raise TypeError(
                "Fallback provider must implement LLMProvider."
            )

        self.primary = primary
        self.fallback = fallback

    def generate(self, prompt: str) -> str:
        """
        Generate using the primary provider.

        If the primary provider fails and a fallback provider is
        configured, retry the same prompt exactly once through the
        fallback provider.
        """

        try:
            return self.primary.generate(prompt)
        except Exception:
            if self.fallback is None:
                raise

            return self.fallback.generate(prompt)