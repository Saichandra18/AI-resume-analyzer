"""Tests for the RAG document parser."""

import pytest

from app.rag.ingestion.parser import DocumentParser


def test_parse_normalizes_line_endings():
    parser = DocumentParser()

    text = "Python\r\nFlask\r\nRAG"

    assert parser.parse(text) == (
        "Python\nFlask\nRAG"
    )


def test_parse_normalizes_carriage_returns():
    parser = DocumentParser()

    text = "Python\rFlask\rRAG"

    assert parser.parse(text) == (
        "Python\nFlask\nRAG"
    )


def test_parse_removes_leading_and_trailing_whitespace():
    parser = DocumentParser()

    text = "  Python  \n  Flask  "

    assert parser.parse(text) == (
        "Python\nFlask"
    )


def test_parse_collapses_spaces_and_tabs():
    parser = DocumentParser()

    text = "Python    Flask\t\tRAG"

    assert parser.parse(text) == (
        "Python Flask RAG"
    )


def test_parse_removes_empty_lines():
    parser = DocumentParser()

    text = "Python\n\n\nFlask"

    assert parser.parse(text) == (
        "Python\nFlask"
    )


def test_parse_rejects_none():
    parser = DocumentParser()

    with pytest.raises(ValueError):
        parser.parse(None)


def test_parse_rejects_non_string():
    parser = DocumentParser()

    with pytest.raises(TypeError):
        parser.parse(["Python", "Flask"])


def test_parse_empty_text():
    parser = DocumentParser()

    assert parser.parse("") == ""