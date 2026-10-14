from anthropic import Anthropic

from .base import LLMProvider


class AnthropicProvider(LLMProvider):
    """
    Anthropic implementation of the generic LLMProvider interface.
    """

    def __init__(
        self,
        api_key=None,
        model=None,
    ):
        if not api_key or not str(api_key).strip():
            raise ValueError(
                "API key is not configured."
            )

        if not model or not str(model).strip():
            raise ValueError(
                "Model must not be empty."
            )

        self.api_key = api_key
        self.model = model

        self.client = Anthropic(
            api_key=self.api_key,
        )

    def generate(self, prompt: str) -> str:
        """
        Generate a text response using the Anthropic Messages API.
        """

        if not prompt or not str(prompt).strip():
            raise ValueError(
                "Prompt must not be empty."
            )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response.content[0].text
