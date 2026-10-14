import pytest

from app.ai.factory import create_llm_provider


def test_openai_requires_api_key(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(
        ValueError,
        match="OPENAI_API_KEY is not configured",
    ):
        create_llm_provider()


def test_openai_compatible_requires_api_key(monkeypatch):
    monkeypatch.setenv(
        "LLM_PROVIDER",
        "openai_compatible",
    )
    monkeypatch.setenv(
        "LLM_MODEL",
        "compatible-model",
    )
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv(
        "LLM_BASE_URL",
        "http://localhost:1234/v1",
    )

    with pytest.raises(
        ValueError,
        match="API key is not configured",
    ):
        create_llm_provider()


def test_openai_compatible_requires_base_url(monkeypatch):
    monkeypatch.setenv(
        "LLM_PROVIDER",
        "openai_compatible",
    )
    monkeypatch.setenv(
        "LLM_MODEL",
        "compatible-model",
    )
    monkeypatch.setenv(
        "LLM_API_KEY",
        "compatible-key",
    )
    monkeypatch.delenv(
        "LLM_BASE_URL",
        raising=False,
    )

    with pytest.raises(
        ValueError,
        match="Base URL must not be empty",
    ):
        create_llm_provider()


def test_local_requires_base_url(monkeypatch):
    monkeypatch.setenv(
        "LLM_PROVIDER",
        "local",
    )
    monkeypatch.setenv(
        "LLM_MODEL",
        "local-model",
    )
    monkeypatch.delenv(
        "LLM_BASE_URL",
        raising=False,
    )
    monkeypatch.delenv(
        "LLM_API_KEY",
        raising=False,
    )

    with pytest.raises(
        ValueError,
        match="Base URL must not be empty",
    ):
        create_llm_provider()


def test_openai_requires_model(monkeypatch):
    monkeypatch.setenv(
        "LLM_PROVIDER",
        "openai",
    )
    monkeypatch.delenv(
        "LLM_MODEL",
        raising=False,
    )
    monkeypatch.delenv(
        "OPENAI_MODEL",
        raising=False,
    )
    monkeypatch.setenv(
        "LLM_API_KEY",
        "test-key",
    )

    with pytest.raises(
        ValueError,
        match="Model must not be empty",
    ):
        create_llm_provider()


def test_openai_compatible_requires_model(monkeypatch):
    monkeypatch.setenv(
        "LLM_PROVIDER",
        "openai_compatible",
    )
    monkeypatch.delenv(
        "LLM_MODEL",
        raising=False,
    )
    monkeypatch.delenv(
        "OPENAI_MODEL",
        raising=False,
    )
    monkeypatch.setenv(
        "LLM_API_KEY",
        "test-key",
    )
    monkeypatch.setenv(
        "LLM_BASE_URL",
        "http://localhost:1234/v1",
    )

    with pytest.raises(
        ValueError,
        match="Model must not be empty",
    ):
        create_llm_provider()


def test_local_requires_model(monkeypatch):
    monkeypatch.setenv(
        "LLM_PROVIDER",
        "local",
    )
    monkeypatch.delenv(
        "LLM_MODEL",
        raising=False,
    )
    monkeypatch.delenv(
        "OPENAI_MODEL",
        raising=False,
    )
    monkeypatch.setenv(
        "LLM_BASE_URL",
        "http://localhost:11434/v1",
    )
    monkeypatch.delenv(
        "LLM_API_KEY",
        raising=False,
    )

    with pytest.raises(
        ValueError,
        match="Model must not be empty",
    ):
        create_llm_provider()


def test_local_allows_missing_api_key(monkeypatch):
    monkeypatch.setenv(
        "LLM_PROVIDER",
        "local",
    )
    monkeypatch.setenv(
        "LLM_MODEL",
        "local-model",
    )
    monkeypatch.setenv(
        "LLM_BASE_URL",
        "http://localhost:11434/v1",
    )
    monkeypatch.delenv(
        "LLM_API_KEY",
        raising=False,
    )

    provider = create_llm_provider()

    assert provider.api_key is None

@pytest.mark.parametrize(
    "api_key",
    [
        "",
        "   ",
    ],
)
def test_openai_rejects_blank_api_key(
    monkeypatch,
    api_key,
):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    monkeypatch.setenv("LLM_API_KEY", api_key)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(
        ValueError,
        match="OPENAI_API_KEY is not configured",
    ):
        create_llm_provider()