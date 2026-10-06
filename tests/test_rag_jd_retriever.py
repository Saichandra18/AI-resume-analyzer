import pytest

from app.rag.retrieval.jd_retriever import JDAwareRetriever


class DummyQueryBuilder:
    def __init__(self, queries=None):
        self.queries = queries or []
        self.received_analysis = None

    def build(self, jd_analysis):
        self.received_analysis = jd_analysis
        return self.queries


class DummyRetrievalService:
    def __init__(self, results=None):
        self.results = results or {}
        self.received_queries = []

    def retrieve(self, query):
        self.received_queries.append(query)
        return self.results.get(query, [])


class DummyChunk:
    def __init__(self, chunk_id):
        self.chunk_id = chunk_id


def test_retriever_builds_queries_from_jd_analysis():
    builder = DummyQueryBuilder(
        queries=["query-1"],
    )
    service = DummyRetrievalService()

    retriever = JDAwareRetriever(
        service,
        builder,
    )

    analysis = {
        "required_skills": ["Python"],
    }

    retriever.retrieve(analysis)

    assert builder.received_analysis == analysis


def test_retriever_executes_each_query():
    queries = [
        "query-1",
        "query-2",
    ]

    builder = DummyQueryBuilder(
        queries=queries,
    )

    service = DummyRetrievalService()

    retriever = JDAwareRetriever(
        service,
        builder,
    )

    retriever.retrieve({})

    assert service.received_queries == queries


def test_retriever_combines_results():
    queries = [
        "query-1",
        "query-2",
    ]

    chunk_one = DummyChunk("chunk-1")
    chunk_two = DummyChunk("chunk-2")

    builder = DummyQueryBuilder(
        queries=queries,
    )

    service = DummyRetrievalService(
        results={
            "query-1": [chunk_one],
            "query-2": [chunk_two],
        }
    )

    retriever = JDAwareRetriever(
        service,
        builder,
    )

    results = retriever.retrieve({})

    assert results == [
        chunk_one,
        chunk_two,
    ]


def test_retriever_removes_duplicate_chunks():
    queries = [
        "query-1",
        "query-2",
    ]

    chunk = DummyChunk("chunk-1")

    builder = DummyQueryBuilder(
        queries=queries,
    )

    service = DummyRetrievalService(
        results={
            "query-1": [chunk],
            "query-2": [chunk],
        }
    )

    retriever = JDAwareRetriever(
        service,
        builder,
    )

    results = retriever.retrieve({})

    assert results == [chunk]


def test_retriever_preserves_first_seen_order():
    queries = [
        "query-1",
        "query-2",
    ]

    chunk_one = DummyChunk("chunk-1")
    chunk_two = DummyChunk("chunk-2")

    builder = DummyQueryBuilder(
        queries=queries,
    )

    service = DummyRetrievalService(
        results={
            "query-1": [chunk_two],
            "query-2": [chunk_one],
        }
    )

    retriever = JDAwareRetriever(
        service,
        builder,
    )

    results = retriever.retrieve({})

    assert results == [
        chunk_two,
        chunk_one,
    ]


def test_retriever_skips_chunks_without_chunk_id():
    class InvalidChunk:
        pass

    builder = DummyQueryBuilder(
        queries=["query"],
    )

    service = DummyRetrievalService(
        results={
            "query": [
                InvalidChunk(),
                DummyChunk("chunk-1"),
            ]
        }
    )

    retriever = JDAwareRetriever(
        service,
        builder,
    )

    results = retriever.retrieve({})

    assert len(results) == 1
    assert results[0].chunk_id == "chunk-1"


def test_retriever_requires_retrieval_service():
    with pytest.raises(ValueError):
        JDAwareRetriever(None)


def test_retriever_validates_retrieval_service():
    with pytest.raises(TypeError):
        JDAwareRetriever(object())