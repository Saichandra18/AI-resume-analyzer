"""Tests for the RAG document cleaner."""

import pytest

from app.rag.ingestion.cleaner import DocumentCleaner


def test_clean_reduces_repeated_spaces():
    cleaner = DocumentCleaner()

    text = "Python     Flask      RAG"

    assert cleaner.clean(text) == (
        "Python Flask RAG"
    )


def test_clean_reduces_repeated_tabs():
    cleaner = DocumentCleaner()

    text = "Python\t\t\tFlask"

    assert cleaner.clean(text) == (
        "Python Flask"
    )


def test_clean_removes_empty_lines():
    cleaner = DocumentCleaner()

    text = "Python\n\n\nFlask"

    assert cleaner.clean(text) == (
        "Python\nFlask"
    )


def test_clean_removes_non_breaking_spaces():
    cleaner = DocumentCleaner()

    text = "Python\u00a0Flask"

    assert cleaner.clean(text) == (
        "Python Flask"
    )


def test_clean_normalizes_long_separators():
    cleaner = DocumentCleaner()

    text = "Python\n========\nFlask"

    assert cleaner.clean(text) == (
        "Python\n---\nFlask"
    )


def test_clean_strips_outer_whitespace():
    cleaner = DocumentCleaner()

    text = "   Python Flask   "

    assert cleaner.clean(text) == (
        "Python Flask"
    )


def test_clean_rejects_none():
    cleaner = DocumentCleaner()

    with pytest.raises(ValueError):
        cleaner.clean(None)


def test_clean_rejects_non_string():
    cleaner = DocumentCleaner()

    with pytest.raises(TypeError):
        cleaner.clean(["Python", "Flask"])


def test_clean_empty_text():
    cleaner = DocumentCleaner()

    assert cleaner.clean("") == ""