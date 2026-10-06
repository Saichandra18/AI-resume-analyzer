from app.rag.models import RetrievedChunk
from app.rag.retrieval.knowledge_retriever import KnowledgeRetriever


class FakeRetrievalService:
    def __init__(self, results=None):
        self.results = results or []
        self.queries = []

    def retrieve(self, query):
        self.queries.append(query)
        return self.results


def test_retriever_requires_retrieval_service():
    try:
        KnowledgeRetriever(None)
    except ValueError as exc:
        assert "retrieval_service" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_retriever_rejects_invalid_retrieval_service():
    try:
        KnowledgeRetriever(object())
    except TypeError as exc:
        assert "retrieve" in str(exc)
    else:
        raise AssertionError("Expected TypeError")


def test_retriever_requires_positive_integer_top_k():
    for value in (0, -1):
        try:
            KnowledgeRetriever(
                FakeRetrievalService(),
                top_k=value,
            )
        except ValueError:
            pass
        else:
            raise AssertionError("Expected ValueError")


def test_retriever_rejects_non_integer_top_k():
    for value in ("5", 1.5, True):
        try:
            KnowledgeRetriever(
                FakeRetrievalService(),
                top_k=value,
            )
        except TypeError:
            pass
        else:
            raise AssertionError("Expected TypeError")


def test_retriever_rejects_invalid_jd_analysis():
    retriever = KnowledgeRetriever(
        FakeRetrievalService()
    )

    try:
        retriever.retrieve(None)
    except TypeError as exc:
        assert "jd_analysis" in str(exc)
    else:
        raise AssertionError("Expected TypeError")


def test_retriever_builds_query_from_required_skills_keywords_and_experience():
    service = FakeRetrievalService()
    retriever = KnowledgeRetriever(
        service,
        top_k=3,
    )

    jd_analysis = {
        "required_skills": ["Python", "SQL"],
        "keywords": ["RAG", "LLM"],
        "experience": ["2 years"],
    }

    retriever.retrieve(jd_analysis)

    query = service.queries[0]

    assert "resume optimization" in query.query
    assert "ATS" in query.query
    assert "job description alignment" in query.query
    assert "Python" in query.query
    assert "SQL" in query.query
    assert "RAG" in query.query
    assert "LLM" in query.query
    assert "2 years" in query.query

def test_retriever_uses_requested_top_k():
    service = FakeRetrievalService()
    retriever = KnowledgeRetriever(
        service,
        top_k=7,
    )

    retriever.retrieve(
        {
            "required_skills": ["Python"],
        }
    )

    assert service.queries[0].top_k == 7


def test_retriever_returns_retrieval_results():
    results = [
        RetrievedChunk(
            chunk_id="ats-guidelines:0",
            text="ATS guidance.",
            score=0.8,
        ),
        RetrievedChunk(
            chunk_id="resume-guidelines:1",
            text="Resume guidance.",
            score=0.7,
        ),
    ]

    service = FakeRetrievalService(results)
    retriever = KnowledgeRetriever(service)

    returned = retriever.retrieve(
        {
            "required_skills": ["Python"],
        }
    )

    assert returned == results
    assert returned is not results


def test_retriever_rejects_invalid_service_result():
    class InvalidService:
        def retrieve(self, query):
            return "invalid"

    retriever = KnowledgeRetriever(
        InvalidService()
    )

    try:
        retriever.retrieve(
            {
                "required_skills": ["Python"],
            }
        )
    except TypeError as exc:
        assert "list or tuple" in str(exc)
    else:
        raise AssertionError("Expected TypeError")


def test_build_query_handles_scalar_values():
    query = KnowledgeRetriever._build_query(
        {
            "required_skills": "Python",
            "keywords": "RAG",
            "experience": "3 years",
        }
    )

    assert "Python" in query
    assert "RAG" in query
    assert "3 years" in query


def test_build_query_handles_missing_fields():
    query = KnowledgeRetriever._build_query({})

    assert "resume optimization" in query
    assert "ATS" in query
    assert "job description alignment" in query


def test_build_query_ignores_empty_values():
    query = KnowledgeRetriever._build_query(
        {
            "required_skills": ["", "Python", "   "],
            "keywords": [],
            "experience": None,
        }
    )

    assert "Python" in query
    assert "resume optimization" in query