"""Configuration for the RAG subsystem."""

import os


class RAGConfig:
    """Runtime configuration for RAG components."""

    def __init__(self):
        self.enabled = self._get_bool(
            "RAG_ENABLED",
            False,
        )

        self.embedding_provider = os.getenv(
            "RAG_EMBEDDING_PROVIDER",
            "local",
        ).strip().lower()

        self.embedding_model = os.getenv(
            "RAG_EMBEDDING_MODEL",
            "default",
        ).strip()

        self.embedding_dimension = self._get_positive_int(
            "RAG_EMBEDDING_DIMENSION",
            384,
        )

    @staticmethod
    def _get_bool(name, default):
        """Read a boolean environment variable."""

        value = os.getenv(name)

        if value is None:
            return default

        return value.strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }

    @staticmethod
    def _get_positive_int(name, default):
        """Read a positive integer environment variable."""

        value = os.getenv(name)

        if value is None:
            return default

        try:
            value = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{name} must be an integer."
            ) from exc

        if value <= 0:
            raise ValueError(
                f"{name} must be positive."
            )

        return value