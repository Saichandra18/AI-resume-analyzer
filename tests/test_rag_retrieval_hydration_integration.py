"""Integration tests for JD-aware retrieval hydration."""

from app.rag.models import (
    DocumentChunk,
    RetrievedChunk,
)
from app.rag.retrieval.hydrator import RetrievalHydrator
from app.rag.retrieval.jd_retriever import JDAwareRetriever
from app.rag.vectorstore.registry import ChunkRegistry


class FakeRetrievalService:
    """Return deterministic retrieval results."""

    def __init__(self, results):
        self.results = results
        self.calls = []

    def retrieve(self, query):
        self.calls.append(query)
        return list(self.results)


class FakeQueryBuilder:
    """Return deterministic retrieval queries."""

    def __init__(self, queries):
        self.queries = queries

    def build(self, jd_analysis):
        return list(self.queries)


def make_registry():
    registry = ChunkRegistry()

    registry.add(
        [
            DocumentChunk(
                chunk_id="chunk-1",
                document_id="doc-1",
                text="Python backend development experience.",
                chunk_index=0,
                metadata={
                    "section": "experience",
                },
            ),
            DocumentChunk(
                chunk_id="chunk-2",
                document_id="doc-1",
                text="Built REST APIs using Flask.",
                chunk_index=1,
                metadata={
                    "section": "projects",
                },
            ),
        ]
    )

    return registry


def test_jd_retriever_hydrates_results():
    service = FakeRetrievalService(
        [
            RetrievedChunk(
                chunk_id="chunk-1",
                text="",
                score=0.95,
            )
        ]
    )

    registry = make_registry()
    hydrator = RetrievalHydrator(registry)

    retriever = JDAwareRetriever(
        retrieval_service=service,
        query_builder=FakeQueryBuilder(["query"]),
        hydrator=hydrator,
    )

    result = retriever.retrieve(
        {
            "required_skills": ["Python"],
        }
    )

    assert len(result) == 1
    assert result[0].chunk_id == "chunk-1"
    assert result[0].text == (
        "Python backend development experience."
    )
    assert result[0].document_id == "doc-1"


def test_jd_retriever_preserves_score_after_hydration():
    service = FakeRetrievalService(
        [
            RetrievedChunk(
                chunk_id="chunk-1",
                text="",
                score=0.8765,
            )
        ]
    )

    retriever = JDAwareRetriever(
        retrieval_service=service,
        query_builder=FakeQueryBuilder(["query"]),
        hydrator=RetrievalHydrator(make_registry()),
    )

    result = retriever.retrieve(
        {
            "required_skills": ["Python"],
        }
    )

    assert result[0].score == 0.8765


def test_jd_retriever_preserves_metadata_after_hydration():
    service = FakeRetrievalService(
        [
            RetrievedChunk(
                chunk_id="chunk-2",
                text="",
                score=0.80,
            )
        ]
    )

    retriever = JDAwareRetriever(
        retrieval_service=service,
        query_builder=FakeQueryBuilder(["query"]),
        hydrator=RetrievalHydrator(make_registry()),
    )

    result = retriever.retrieve(
        {
            "required_skills": ["Flask"],
        }
    )

    assert result[0].metadata == {
        "section": "projects",
    }


def test_jd_retriever_without_hydrator_preserves_existing_behavior():
    original = RetrievedChunk(
        chunk_id="chunk-1",
        text="",
        score=0.95,
    )

    service = FakeRetrievalService([original])

    retriever = JDAwareRetriever(
        retrieval_service=service,
        query_builder=FakeQueryBuilder(["query"]),
    )

    result = retriever.retrieve(
        {
            "required_skills": ["Python"],
        }
    )

    assert result == [original]
    assert result[0].text == ""


def test_hydration_happens_after_deduplication():
    results = [
        RetrievedChunk(
            chunk_id="chunk-1",
            text="",
            score=0.95,
        )
    ]

    class CountingHydrator:
        def __init__(self):
            self.calls = 0
            self.received = None

        def hydrate(self, chunks):
            self.calls += 1
            self.received = list(chunks)
            return list(chunks)

    hydrator = CountingHydrator()

    service = FakeRetrievalService(results)

    retriever = JDAwareRetriever(
        retrieval_service=service,
        query_builder=FakeQueryBuilder(
            ["query-1", "query-2"]
        ),
        hydrator=hydrator,
    )

    result = retriever.retrieve(
        {
            "required_skills": ["Python"],
        }
    )

    assert hydrator.calls == 1
    assert len(hydrator.received) == 1
    assert len(result) == 1


def test_invalid_hydrator_is_rejected():
    service = FakeRetrievalService([])

    class InvalidHydrator:
        pass

    try:
        JDAwareRetriever(
            retrieval_service=service,
            hydrator=InvalidHydrator(),
        )
    except TypeError as exc:
        assert "hydrate" in str(exc)
    else:
        raise AssertionError(
            "Expected TypeError for invalid hydrator."
        )


def test_missing_registry_chunk_is_not_returned():
    service = FakeRetrievalService(
        [
            RetrievedChunk(
                chunk_id="missing",
                text="",
                score=0.95,
            )
        ]
    )

    retriever = JDAwareRetriever(
        retrieval_service=service,
        query_builder=FakeQueryBuilder(["query"]),
        hydrator=RetrievalHydrator(
            make_registry()
        ),
    )

    result = retriever.retrieve(
        {
            "required_skills": ["Python"],
        }
    )

    assert result == []


def test_multiple_retrieved_chunks_are_hydrated():
    service = FakeRetrievalService(
        [
            RetrievedChunk(
                chunk_id="chunk-1",
                text="",
                score=0.95,
            ),
            RetrievedChunk(
                chunk_id="chunk-2",
                text="",
                score=0.85,
            ),
        ]
    )

    retriever = JDAwareRetriever(
        retrieval_service=service,
        query_builder=FakeQueryBuilder(["query"]),
        hydrator=RetrievalHydrator(
            make_registry()
        ),
    )

    result = retriever.retrieve(
        {
            "required_skills": [
                "Python",
                "Flask",
            ],
        }
    )

    assert len(result) == 2
    assert result[0].text == (
        "Python backend development experience."
    )
    assert result[1].text == (
        "Built REST APIs using Flask."
    )