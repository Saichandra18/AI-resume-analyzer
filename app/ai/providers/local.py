from openai import OpenAI

from .base import LLMProvider


class LocalProvider(LLMProvider):
    """Provider for local LLMs exposing an OpenAI-compatible API."""

    def __init__(
        self,
        model=None,
        base_url=None,
        api_key=None,
    ):
        if not model or not str(model).strip():
            raise ValueError("Model must not be empty.")

        if not base_url or not str(base_url).strip():
            raise ValueError("Base URL must not be empty.")

        self.model = model
        self.base_url = base_url
        self.api_key = api_key

        # Local OpenAI-compatible servers commonly don't require
        # authentication, but the OpenAI SDK expects an API key.
        # Pass a placeholder explicitly instead of modifying the
        # process-wide OPENAI_API_KEY environment variable.
        client_api_key = (
            api_key if api_key is not None else "local"
        )

        self.client = OpenAI(
            api_key=client_api_key,
            base_url=self.base_url,
        )

    def generate(self, prompt: str) -> str:
        if not prompt or not str(prompt).strip():
            raise ValueError("Prompt must not be empty.")

        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )

        return response.output_text
