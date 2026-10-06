"""Tests for the RAG document loader."""

from pathlib import Path

import pytest

from app.rag.ingestion.loader import DocumentLoader


def test_load_txt(tmp_path):
    file_path = tmp_path / "knowledge.txt"
    file_path.write_text(
        "Python is a programming language.",
        encoding="utf-8",
    )

    loader = DocumentLoader()

    assert loader.load(file_path) == (
        "Python is a programming language."
    )


def test_load_markdown(tmp_path):
    file_path = tmp_path / "knowledge.md"
    file_path.write_text(
        "# Python\n\nPython is widely used.",
        encoding="utf-8",
    )

    loader = DocumentLoader()

    assert loader.load(file_path) == (
        "# Python\n\nPython is widely used."
    )


def test_missing_file_raises_error(tmp_path):
    loader = DocumentLoader()

    with pytest.raises(FileNotFoundError):
        loader.load(tmp_path / "missing.txt")


def test_directory_raises_error(tmp_path):
    loader = DocumentLoader()

    with pytest.raises(ValueError):
        loader.load(tmp_path)


def test_unsupported_extension_raises_error(tmp_path):
    file_path = tmp_path / "knowledge.csv"
    file_path.write_text(
        "skill,level",
        encoding="utf-8",
    )

    loader = DocumentLoader()

    with pytest.raises(ValueError):
        loader.load(file_path)


def test_extension_check_is_case_insensitive(tmp_path):
    file_path = tmp_path / "knowledge.TXT"
    file_path.write_text(
        "Case insensitive extension.",
        encoding="utf-8",
    )

    loader = DocumentLoader()

    assert loader.load(file_path) == (
        "Case insensitive extension."
    )