"""Tests for the knowledge guidance adapter."""

import pytest

from app.rag.models import RetrievedChunk
from app.rag.optimization.knowledge_guidance import (
    KnowledgeGuidanceAdapter,
)


def make_chunk(
    chunk_id="chunk-1",
    document_id="ats-guidelines",
    text="Use relevant keywords naturally.",
    score=0.91,
    metadata=None,
):
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id=document_id,
        text=text,
        score=score,
        metadata=metadata or {},
    )


def test_adapter_builds_guidance_from_retrieved_chunks():
    adapter = KnowledgeGuidanceAdapter()

    chunks = [
        make_chunk(
            metadata={
                "source_category": "ats",
            }
        )
    ]

    result = adapter.build(chunks)

    assert "guidance" in result
    assert len(result["guidance"]) == 1

    guidance = result["guidance"][0]

    assert guidance["text"] == (
        "Use relevant keywords naturally."
    )
    assert guidance["source_chunk_id"] == "chunk-1"
    assert guidance["document_id"] == "ats-guidelines"
    assert guidance["score"] == 0.91
    assert guidance["category"] == "ats"


def test_adapter_preserves_source_metadata():
    adapter = KnowledgeGuidanceAdapter()

    chunks = [
        make_chunk(
            metadata={
                "source_category": "resume",
                "source_id": "resume-guidelines",
                "custom": "value",
            }
        )
    ]

    result = adapter.build(chunks)

    metadata = result["guidance"][0]["metadata"]

    assert metadata["source_category"] == "resume"
    assert metadata["source_id"] == (
        "resume-guidelines"
    )
    assert metadata["custom"] == "value"


def test_adapter_defaults_category_to_general():
    adapter = KnowledgeGuidanceAdapter()

    result = adapter.build(
        [
            make_chunk(
                metadata={}
            )
        ]
    )

    assert result["guidance"][0]["category"] == (
        "general"
    )


def test_adapter_uses_category_when_source_category_missing():
    adapter = KnowledgeGuidanceAdapter()

    result = adapter.build(
        [
            make_chunk(
                metadata={
                    "category": "role"
                }
            )
        ]
    )

    assert result["guidance"][0]["category"] == (
        "role"
    )


def test_adapter_handles_multiple_categories():
    adapter = KnowledgeGuidanceAdapter()

    chunks = [
        make_chunk(
            chunk_id="ats-1",
            metadata={
                "source_category": "ats"
            }
        ),
        make_chunk(
            chunk_id="resume-1",
            document_id="resume-guidelines",
            metadata={
                "source_category": "resume"
            }
        ),
        make_chunk(
            chunk_id="role-1",
            document_id="role-guidelines",
            metadata={
                "source_category": "role"
            }
        ),
    ]

    result = adapter.build(chunks)

    assert [
        item["category"]
        for item in result["guidance"]
    ] == [
        "ats",
        "resume",
        "role",
    ]


def test_adapter_adds_metadata():
    adapter = KnowledgeGuidanceAdapter()

    result = adapter.build(
        [
            make_chunk()
        ],
        metadata={
            "query_type": "jd_optimization"
        },
    )

    assert result["metadata"]["knowledge_base"] is True
    assert result["metadata"]["guidance_count"] == 1
    assert result["metadata"]["query_type"] == (
        "jd_optimization"
    )


def test_adapter_defensively_copies_metadata():
    adapter = KnowledgeGuidanceAdapter()

    source_metadata = {
        "source_category": "ats",
        "nested": {
            "value": "original"
        },
    }

    result = adapter.build(
        [
            make_chunk(
                metadata=source_metadata
            )
        ]
    )

    result["guidance"][0]["metadata"]["nested"][
        "value"
    ] = "changed"

    assert source_metadata["nested"]["value"] == (
        "original"
    )


def test_adapter_requires_list_or_tuple():
    adapter = KnowledgeGuidanceAdapter()

    with pytest.raises(TypeError):
        adapter.build("invalid")


def test_adapter_requires_retrieved_chunk_objects():
    adapter = KnowledgeGuidanceAdapter()

    with pytest.raises(TypeError):
        adapter.build(
            [
                {
                    "chunk_id": "chunk-1",
                    "text": "guidance",
                }
            ]
        )


def test_adapter_returns_empty_guidance_for_empty_input():
    adapter = KnowledgeGuidanceAdapter()

    result = adapter.build([])

    assert result["guidance"] == []
    assert result["metadata"]["knowledge_base"] is True
    assert result["metadata"]["guidance_count"] == 0


def test_adapter_does_not_create_grounding_fields():
    adapter = KnowledgeGuidanceAdapter()

    result = adapter.build(
        [
            make_chunk(
                metadata={
                    "source_category": "ats"
                }
            )
        ]
    )

    guidance = result["guidance"][0]

    assert "evidence_id" not in guidance
    assert "claim" not in guidance
    assert "confidence" not in guidance
    assert "grounding" not in guidance