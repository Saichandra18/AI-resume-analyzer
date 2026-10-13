"""Tests for RAG configuration."""

import pytest

from app.rag.config import RAGConfig


def test_rag_is_disabled_by_default(monkeypatch):
    monkeypatch.delenv(
        "RAG_ENABLED",
        raising=False,
    )

    config = RAGConfig()

    assert config.enabled is False


def test_rag_enabled_accepts_true_values(monkeypatch):
    for value in (
        "1",
        "true",
        "TRUE",
        "yes",
        "on",
    ):
        monkeypatch.setenv(
            "RAG_ENABLED",
            value,
        )

        config = RAGConfig()

        assert config.enabled is True


def test_rag_enabled_rejects_false_values(monkeypatch):
    for value in (
        "0",
        "false",
        "no",
        "off",
    ):
        monkeypatch.setenv(
            "RAG_ENABLED",
            value,
        )

        config = RAGConfig()

        assert config.enabled is False


def test_default_embedding_configuration(monkeypatch):
    monkeypatch.delenv(
        "RAG_EMBEDDING_PROVIDER",
        raising=False,
    )
    monkeypatch.delenv(
        "RAG_EMBEDDING_MODEL",
        raising=False,
    )
    monkeypatch.delenv(
        "RAG_EMBEDDING_DIMENSION",
        raising=False,
    )

    config = RAGConfig()

    assert config.embedding_provider == "local"
    assert config.embedding_model == "default"
    assert config.embedding_dimension == 384


def test_custom_embedding_configuration(monkeypatch):
    monkeypatch.setenv(
        "RAG_EMBEDDING_PROVIDER",
        " OpenAI ",
    )
    monkeypatch.setenv(
        "RAG_EMBEDDING_MODEL",
        " text-embedding-model ",
    )
    monkeypatch.setenv(
        "RAG_EMBEDDING_DIMENSION",
        "1536",
    )

    config = RAGConfig()

    assert config.embedding_provider == "openai"
    assert config.embedding_model == "text-embedding-model"
    assert config.embedding_dimension == 1536


def test_invalid_embedding_dimension_raises_error(monkeypatch):
    monkeypatch.setenv(
        "RAG_EMBEDDING_DIMENSION",
        "invalid",
    )

    with pytest.raises(ValueError):
        RAGConfig()


def test_non_positive_embedding_dimension_raises_error(
    monkeypatch,
):
    for value in ("0", "-1"):
        monkeypatch.setenv(
            "RAG_EMBEDDING_DIMENSION",
            value,
        )

        with pytest.raises(ValueError):
            RAGConfig()


def test_boolean_configuration_is_case_insensitive(
    monkeypatch,
):
    monkeypatch.setenv(
        "RAG_ENABLED",
        " TrUe ",
    )

    config = RAGConfig()

    assert config.enabled is True


@pytest.mark.parametrize(
    "value",
    [
        "maybe",
        "treu",
        "",
        "enabled",
        "2",
    ],
)
def test_invalid_rag_enabled_value_raises_error(
    monkeypatch,
    value,
):
    monkeypatch.setenv("RAG_ENABLED", value)

    with pytest.raises(
        ValueError,
        match="RAG_ENABLED must be a boolean value",
    ):
        RAGConfig()
