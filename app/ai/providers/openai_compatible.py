from openai import OpenAI

from .base import LLMProvider


class OpenAICompatibleProvider(LLMProvider):
    """
    Provider implementation for APIs exposing an
    OpenAI-compatible interface.

    Unlike OpenAIProvider, this provider requires an explicit
    base URL so it can communicate with compatible endpoints.
    """

    def __init__(
        self,
        api_key=None,
        model=None,
        base_url=None,
    ):
        if not api_key or not str(api_key).strip():
            raise ValueError("API key is not configured.")

        if not model or not str(model).strip():
            raise ValueError("Model must not be empty.")

        if not base_url or not str(base_url).strip():
            raise ValueError("Base URL must not be empty.")

        self.api_key = api_key
        self.model = model
        self.base_url = base_url

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    def generate(self, prompt: str) -> str:
        """
        Generate text using an OpenAI-compatible Responses API.
        """

        if not prompt or not str(prompt).strip():
            raise ValueError("Prompt must not be empty.")

        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )

        return response.output_text