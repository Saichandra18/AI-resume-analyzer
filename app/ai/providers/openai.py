import os

from openai import OpenAI

from .base import LLMProvider


class OpenAIProvider(LLMProvider):
    """
    OpenAI implementation of the generic LLMProvider interface.
    """

    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-5.6-luna")

        if not self.api_key or not str(self.api_key).strip():
            raise ValueError("OPENAI_API_KEY is not configured.")

        self.client = OpenAI(api_key=self.api_key)

    def generate(self, prompt: str) -> str:
        """
        Generate a text response using the OpenAI Responses API.
        """

        if not prompt or not str(prompt).strip():
            raise ValueError("Prompt must not be empty.")

        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )

        return response.output_text