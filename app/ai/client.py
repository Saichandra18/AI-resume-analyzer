import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


class OpenAIClient:
    """Thin wrapper around the OpenAI Responses API."""

    def __init__(
        self,
        api_key=None,
        model=None,
    ):
        self.api_key = (
            api_key
            or os.getenv("OPENAI_API_KEY")
        )

        self.model = (
            model
            or os.getenv(
                "OPENAI_MODEL",
                "gpt-5.6-luna",
            )
        )

        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY is not configured."
            )

        self.client = OpenAI(
            api_key=self.api_key
        )

    def generate(
        self,
        prompt,
    ):
        """Generate a text response from OpenAI."""

        if not prompt or not str(prompt).strip():
            raise ValueError(
                "Prompt must not be empty."
            )

        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )

        return response.output_text