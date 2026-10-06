
import os

from dotenv import load_dotenv


load_dotenv()


class Config:
    ENV = os.getenv("FLASK_ENV", "development").lower()

    _secret_key = os.getenv("SECRET_KEY")

    if ENV == "production" and not _secret_key:
        raise RuntimeError(
            "SECRET_KEY must be set when FLASK_ENV=production."
        )

    SECRET_KEY = _secret_key or "development-secret-key"

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv(
        "OPENAI_MODEL",
        "gpt-5.6-luna",
    )

    RAG_ENABLED = os.getenv(
        "RAG_ENABLED",
        "false",
    ).lower() in {
        "1",
        "true",
        "yes",
        "on",
    }

    RAG_EMBEDDING_PROVIDER = os.getenv(
        "RAG_EMBEDDING_PROVIDER",
        "local",
    )

    RAG_EMBEDDING_MODEL = os.getenv(
        "RAG_EMBEDDING_MODEL",
        "default",
    )

    RAG_EMBEDDING_DIMENSION = int(
        os.getenv(
            "RAG_EMBEDDING_DIMENSION",
            "384",
        )
    )

    RAG_KNOWLEDGE_INDEX_PATH = os.getenv(
        "RAG_KNOWLEDGE_INDEX_PATH"
    )

    FLASK_DEBUG = os.getenv(
        "FLASK_DEBUG",
        "false",
    ).lower() in {
        "1",
        "true",
        "yes",
        "on",
    }

