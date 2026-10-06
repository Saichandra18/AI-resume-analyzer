import pytest

from app.rag.models import RetrievalQuery
from app.rag.retrieval.query_builder import JDQueryBuilder


def test_builds_required_skills_query():
    builder = JDQueryBuilder()

    results = builder.build({
        "required_skills": [
            "Python",
            "Flask",
        ],
    })

    assert len(results) == 1
    assert isinstance(results[0], RetrievalQuery)
    assert results[0].query == (
        "Required skills: Python, Flask"
    )


def test_builds_multiple_query_categories():
    builder = JDQueryBuilder()

    results = builder.build({
        "required_skills": ["Python"],
        "technical_keywords": ["RAG"],
        "responsibilities": ["Build APIs"],
    })

    assert len(results) == 3

    assert results[0].query == (
        "Required skills: Python"
    )

    assert results[1].query == (
        "Technical keywords: RAG"
    )

    assert results[2].query == (
        "Responsibilities: Build APIs"
    )


def test_skips_missing_fields():
    builder = JDQueryBuilder()

    results = builder.build({
        "required_skills": ["Python"],
    })

    assert len(results) == 1


def test_skips_empty_values():
    builder = JDQueryBuilder()

    results = builder.build({
        "required_skills": [],
        "technical_keywords": "",
    })

    assert results == []


def test_normalizes_string_values():
    builder = JDQueryBuilder()

    results = builder.build({
        "required_skills": "  Python   Flask  ",
    })

    assert results[0].query == (
        "Required skills: Python Flask"
    )


def test_normalizes_list_values():
    builder = JDQueryBuilder()

    results = builder.build({
        "tools": [
            " Docker ",
            None,
            " Kubernetes ",
        ],
    })

    assert results[0].query == (
        "Tools and platforms: Docker, Kubernetes"
    )


def test_rejects_none():
    builder = JDQueryBuilder()

    with pytest.raises(ValueError):
        builder.build(None)


def test_rejects_non_dictionary():
    builder = JDQueryBuilder()

    with pytest.raises(TypeError):
        builder.build("Python Flask")