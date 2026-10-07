from .providers import OpenAIProvider


class OpenAIClient:
    """
    Backward-compatible wrapper around OpenAIProvider.

    Existing application code can continue using OpenAIClient
    while the underlying architecture uses the generic
    LLMProvider abstraction.
    """

    def __init__(self, api_key=None, model=None):
        self.provider = OpenAIProvider(
            api_key=api_key,
            model=model,
        )

    @property
    def api_key(self):
        return self.provider.api_key

    @property
    def model(self):
        return self.provider.model

    @property
    def client(self):
        return self.provider.client

    @client.setter
    def client(self, value):
        self.provider.client = value

    def generate(self, prompt):
        """Generate text through the configured LLM provider."""
        return self.provider.generate(prompt)