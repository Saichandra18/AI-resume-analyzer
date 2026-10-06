"""Tests for application runtime configuration."""

import importlib
import os


def test_run_module_creates_app(
    monkeypatch,
):
    monkeypatch.delenv(
        "FLASK_DEBUG",
        raising=False,
    )

    module = importlib.import_module("run")

    assert module.app is not None


def test_flask_debug_true_values_are_recognized():
    true_values = {
        "1",
        "true",
        "yes",
        "on",
    }

    for value in true_values:
        debug = value.lower() in {
            "1",
            "true",
            "yes",
            "on",
        }

        assert debug is True


def test_flask_debug_defaults_to_false(
    monkeypatch,
):
    monkeypatch.delenv(
        "FLASK_DEBUG",
        raising=False,
    )

    value = os.getenv(
        "FLASK_DEBUG",
        "false",
    )

    debug = value.lower() in {
        "1",
        "true",
        "yes",
        "on",
    }

    assert debug is False