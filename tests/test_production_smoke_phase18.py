import os

import pytest


def test_production_requires_secret_key(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.delenv("SECRET_KEY", raising=False)

    with pytest.raises(RuntimeError, match="SECRET_KEY must be set"):
        import config

        # Force Config evaluation after environment changes.
        import importlib

        importlib.reload(config)


def test_production_configuration(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.setenv("SECRET_KEY", "phase18-test-secret")
    monkeypatch.setenv("RAG_ENABLED", "false")
    monkeypatch.setenv("FLASK_DEBUG", "false")

    import config

    import importlib

    importlib.reload(config)

    assert config.Config.ENV == "production"
    assert config.Config.RAG_ENABLED is False
    assert config.Config.FLASK_DEBUG is False
    assert config.Config.SECRET_KEY == "phase18-test-secret"


def test_production_app_creation(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.setenv("SECRET_KEY", "phase18-test-secret")
    monkeypatch.setenv("RAG_ENABLED", "false")
    monkeypatch.setenv("FLASK_DEBUG", "false")

    import config

    import importlib

    importlib.reload(config)

    from app import create_app

    app = create_app()

    assert app is not None
    assert app.debug is False


def test_production_root_endpoint(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.setenv("SECRET_KEY", "phase18-test-secret")
    monkeypatch.setenv("RAG_ENABLED", "false")
    monkeypatch.setenv("FLASK_DEBUG", "false")

    import config

    import importlib

    importlib.reload(config)

    from app import create_app

    app = create_app()

    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"AI Resume Analyzer" in response.data


def test_production_job_description_validation(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.setenv("SECRET_KEY", "phase18-test-secret")
    monkeypatch.setenv("RAG_ENABLED", "false")
    monkeypatch.setenv("FLASK_DEBUG", "false")

    import config

    import importlib

    importlib.reload(config)

    from app import create_app

    app = create_app()

    client = app.test_client()

    response = client.post(
        "/api/job-description",
        json={},
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert "message" in data


def test_production_generation_validation(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.setenv("SECRET_KEY", "phase18-test-secret")
    monkeypatch.setenv("RAG_ENABLED", "false")
    monkeypatch.setenv("FLASK_DEBUG", "false")

    import config

    import importlib

    importlib.reload(config)

    from app import create_app

    app = create_app()

    client = app.test_client()

    response = client.post(
        "/api/resume/generate",
        json={
            "resume_text": "",
            "job_description": "",
            "target_pages": 1,
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert data["message"] == "Resume text is required."

    assert "Traceback" not in response.get_data(as_text=True)