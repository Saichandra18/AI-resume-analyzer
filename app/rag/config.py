
"""Configuration for the RAG subsystem."""

import os


class RAGConfig:
    """Runtime configuration for RAG components."""

    def __init__(self):
        self.enabled = self._get_bool("RAG_ENABLED", False)

        self.embedding_provider = self._get_string(
            "RAG_EMBEDDING_PROVIDER", "local"
        ).lower()

        self.embedding_model = self._get_string(
            "RAG_EMBEDDING_MODEL", "default"
        )

        self.embedding_dimension = self._get_positive_int(
            "RAG_EMBEDDING_DIMENSION", 384
        )

    @staticmethod
    def _get_string(name, default):
        """Read a non-empty string environment variable."""
        value = os.getenv(name, default)

        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must not be empty.")

        return value.strip()

    @staticmethod
    def _get_bool(name, default):
        """Read a boolean environment variable."""
        value = os.getenv(name)

        if value is None:
            return default

        return value.strip().lower() in {
            "1", "true", "yes", "on"
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
            raise ValueError(f"{name} must be positive.")

        return value
