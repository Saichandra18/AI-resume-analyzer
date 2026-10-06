"""Deterministic local embedding provider."""

import hashlib
import math

from app.rag.interfaces import EmbeddingProvider


class LocalEmbeddingProvider(EmbeddingProvider):
    """Generate deterministic embeddings without external APIs."""

    def __init__(self, dimension=384):
        if not isinstance(dimension, int):
            raise TypeError(
                "dimension must be an integer."
            )

        if dimension <= 0:
            raise ValueError(
                "dimension must be positive."
            )

        self.dimension = dimension

    def generate_embedding(self, text):
        """Generate a deterministic embedding for one text."""

        if not isinstance(text, str):
            raise TypeError(
                "text must be a string."
            )

        if not text.strip():
            raise ValueError(
                "text cannot be empty."
            )

        values = []

        for index in range(self.dimension):
            digest = hashlib.sha256(
                f"{text}:{index}".encode("utf-8")
            ).digest()

            integer = int.from_bytes(
                digest[:8],
                byteorder="big",
            )

            value = (
                (integer / ((1 << 64) - 1)) * 2
            ) - 1

            values.append(value)

        magnitude = math.sqrt(
            sum(value * value for value in values)
        )

        if magnitude == 0:
            return [0.0] * self.dimension

        return [
            value / magnitude
            for value in values
        ]

    def generate_embeddings(self, texts):
        """Generate embeddings for multiple texts."""

        if not isinstance(texts, (list, tuple)):
            raise TypeError(
                "texts must be a list or tuple."
            )

        return [
            self.generate_embedding(text)
            for text in texts
        ]