from app.rag.models import RetrievedChunk
from app.rag.optimization.resume_context import (
    ResumeContextBuilder,
)
from app.rag.retrieval.jd_retriever import (
    JDAwareRetriever,
)


class FakeQuery:
    def __init__(self, query):
        self.query = query


class FakeQueryBuilder:
    def build(self, jd_analysis):
        return [
            FakeQuery("python flask"),
            FakeQuery("rest api"),
        ]


class FakeRetrievalService:
    def __init__(self):
        self.queries = []

    def retrieve(self, query):
        self.queries.append(query)

        if "python flask" == query.query:
            return [
                RetrievedChunk(
                    chunk_id="chunk-python",
                    text="Python Flask experience",
                    score=0.9,
                )
            ]

        if "rest api" == query.query:
            return [
                RetrievedChunk(
                    chunk_id="chunk-api",
                    text="REST API experience",
                    score=0.8,
                )
            ]

        return [
            RetrievedChunk(
                chunk_id="chunk-candidate",
                text="Python backend developer",
                score=0.7,
            )
        ]


def test_resume_context_adds_candidate_query():
    service = FakeRetrievalService()

    retriever = JDAwareRetriever(
        retrieval_service=service,
        query_builder=FakeQueryBuilder(),
    )

    resume_data = {
        "summary": "Python backend developer",
        "skills": [
            "Python",
            "Flask",
        ],
    }

    retriever.retrieve(
        {"required_skills": ["Python"]},
        resume_context=resume_data,
    )

    assert len(service.queries) == 3

    query_texts = [
        query.query
        for query in service.queries
    ]

    assert "python flask" in query_texts
    assert "rest api" in query_texts

    candidate_query = query_texts[-1]

    assert "Python backend developer" in candidate_query
    assert "Python" in candidate_query
    assert "Flask" in candidate_query


def test_existing_jd_queries_are_preserved():
    service = FakeRetrievalService()

    retriever = JDAwareRetriever(
        retrieval_service=service,
        query_builder=FakeQueryBuilder(),
    )

    retriever.retrieve(
        {"required_skills": ["Python"]},
        resume_context={
            "skills": ["Python"]
        },
    )

    query_texts = [
        query.query
        for query in service.queries
    ]

    assert query_texts[0] == "python flask"
    assert query_texts[1] == "rest api"


def test_resume_context_is_optional():
    service = FakeRetrievalService()

    retriever = JDAwareRetriever(
        retrieval_service=service,
        query_builder=FakeQueryBuilder(),
    )

    results = retriever.retrieve(
        {"required_skills": ["Python"]}
    )

    assert len(service.queries) == 2
    assert len(results) == 2


def test_empty_resume_context_does_not_add_query():
    service = FakeRetrievalService()

    retriever = JDAwareRetriever(
        retrieval_service=service,
        query_builder=FakeQueryBuilder(),
    )

    retriever.retrieve(
        {"required_skills": ["Python"]},
        resume_context={
            "summary": "",
            "skills": [],
            "experience": [],
            "projects": [],
            "education": [],
            "certifications": [],
        },
    )

    assert len(service.queries) == 2


def test_duplicate_chunks_are_removed():
    class DuplicateRetrievalService:
        def __init__(self):
            self.queries = []

        def retrieve(self, query):
            self.queries.append(query)

            return [
                RetrievedChunk(
                    chunk_id="same-chunk",
                    text="Shared evidence",
                    score=0.9,
                )
            ]

    service = DuplicateRetrievalService()

    retriever = JDAwareRetriever(
        retrieval_service=service,
        query_builder=FakeQueryBuilder(),
    )

    results = retriever.retrieve(
        {"required_skills": ["Python"]},
        resume_context={
            "skills": ["Python"]
        },
    )

    assert len(service.queries) == 3
    assert len(results) == 1
    assert results[0].chunk_id == "same-chunk"


def test_resume_context_builder_can_be_injected():
    class CustomResumeContextBuilder:
        def build(self, resume_data):
            return {
                "summary": "CUSTOM CONTEXT"
            }

        def to_query_text(self, context):
            return "CUSTOM CONTEXT"

    service = FakeRetrievalService()

    retriever = JDAwareRetriever(
        retrieval_service=service,
        query_builder=FakeQueryBuilder(),
        resume_context_builder=(
            CustomResumeContextBuilder()
        ),
    )

    retriever.retrieve(
        {"required_skills": ["Python"]},
        resume_context={
            "skills": ["ignored"]
        },
    )

    assert service.queries[-1].query == (
        "CUSTOM CONTEXT"
    )


def test_resume_context_dictionary_is_used_directly():
    service = FakeRetrievalService()

    builder = ResumeContextBuilder()

    retriever = JDAwareRetriever(
        retrieval_service=service,
        query_builder=FakeQueryBuilder(),
        resume_context_builder=builder,
    )

    context = {
        "summary": "Python developer",
        "skills": ["Python"],
        "experience": [],
        "projects": [],
        "education": [],
        "certifications": [],
    }

    retriever.retrieve(
        {"required_skills": ["Python"]},
        resume_context=context,
    )

    assert "Python developer" in (
        service.queries[-1].query
    )


def test_retrieval_results_remain_unique_with_resume_query():
    service = FakeRetrievalService()

    retriever = JDAwareRetriever(
        retrieval_service=service,
        query_builder=FakeQueryBuilder(),
    )

    results = retriever.retrieve(
        {"required_skills": ["Python"]},
        resume_context={
            "summary": "Python backend developer",
            "skills": ["Python", "Flask"],
        },
    )

    chunk_ids = [
        chunk.chunk_id
        for chunk in results
    ]

    assert len(chunk_ids) == len(
        set(chunk_ids)
    )