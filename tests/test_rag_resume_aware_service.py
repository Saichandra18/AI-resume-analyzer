from app.rag.config import RAGConfig
from app.rag.models import DocumentChunk
from app.rag.optimization.service import (
    RAGOptimizationService,
)


class TestEmbeddingProvider:
    def generate_embeddings(self, texts):
        return [[1.0, 0.0, 0.0] for _ in texts]

    def generate_embedding(self, text):
        return [1.0, 0.0, 0.0]


class FakeOrchestrator:
    def __init__(self):
        self.received_jd_analysis = None
        self.received_resume_context = None

    def optimize(
        self,
        jd_analysis,
        resume_context=None,
    ):
        self.received_jd_analysis = jd_analysis
        self.received_resume_context = resume_context

        return {
            "retrieved_chunks": [],
            "evidence": [],
            "recommendations": [],
            "safety_results": [],
            "signals": [],
            "phase11_payload": {
                "skills_to_emphasize": [
                    "Python"
                ]
            },
            "metadata": {},
        }


class TestConfig:
    enabled = True
    embedding_dimension = 3


def test_service_builds_resume_context():
    orchestrator = FakeOrchestrator()

    service = RAGOptimizationService(
        config=TestConfig(),
        embedding_provider=TestEmbeddingProvider(),
        orchestrator=orchestrator,
    )

    resume_data = {
        "summary": "Python backend developer",
        "skills": [
            "Python",
            "Flask",
        ],
        "experience": [
            {
                "job_title": "Backend Developer",
                "company": "Example",
                "bullets": [
                    "Built REST APIs"
                ],
            }
        ],
        "projects": [],
        "education": [],
        "certifications": [],
    }

    jd_analysis = {
        "required_skills": [
            "Python",
            "Flask",
        ]
    }

    service.optimize(
        jd_analysis=jd_analysis,
        resume_data=resume_data,
    )

    assert (
        orchestrator.received_resume_context
        is not None
    )

    assert (
        orchestrator.received_resume_context[
            "summary"
        ]
        == "Python backend developer"
    )

    assert (
        orchestrator.received_resume_context[
            "skills"
        ]
        == ["Python", "Flask"]
    )


def test_service_passes_jd_analysis_unchanged():
    orchestrator = FakeOrchestrator()

    service = RAGOptimizationService(
        config=TestConfig(),
        embedding_provider=TestEmbeddingProvider(),
        orchestrator=orchestrator,
    )

    jd_analysis = {
        "required_skills": ["Python"],
        "job_title": "Backend Engineer",
    }

    service.optimize(
        jd_analysis=jd_analysis,
        resume_data={
            "skills": ["Python"]
        },
    )

    assert (
        orchestrator.received_jd_analysis
        == jd_analysis
    )


def test_service_does_not_mutate_resume_data():
    orchestrator = FakeOrchestrator()

    service = RAGOptimizationService(
        config=TestConfig(),
        embedding_provider=TestEmbeddingProvider(),
        orchestrator=orchestrator,
    )

    resume_data = {
        "summary": "Python developer",
        "skills": ["Python"],
        "experience": [
            {
                "job_title": "Developer",
                "bullets": [
                    "Built APIs"
                ],
            }
        ],
    }

    original = {
        "summary": "Python developer",
        "skills": ["Python"],
        "experience": [
            {
                "job_title": "Developer",
                "bullets": [
                    "Built APIs"
                ],
            }
        ],
    }

    service.optimize(
        jd_analysis={
            "required_skills": ["Python"]
        },
        resume_data=resume_data,
    )

    assert resume_data == original


def test_service_without_resume_data_remains_compatible():
    orchestrator = FakeOrchestrator()

    service = RAGOptimizationService(
        config=TestConfig(),
        embedding_provider=TestEmbeddingProvider(),
        orchestrator=orchestrator,
    )

    result = service.optimize(
        jd_analysis={
            "required_skills": ["Python"]
        }
    )

    assert (
        orchestrator.received_resume_context
        is None
    )

    assert result["phase11_payload"] == {
        "skills_to_emphasize": [
            "Python"
        ]
    }


def test_service_returns_phase11_payload():
    orchestrator = FakeOrchestrator()

    service = RAGOptimizationService(
        config=TestConfig(),
        embedding_provider=TestEmbeddingProvider(),
        orchestrator=orchestrator,
    )

    result = service.optimize(
        jd_analysis={
            "required_skills": ["Python"]
        },
        resume_data={
            "skills": [
                "Python",
                "Flask",
            ]
        },
    )

    assert result["phase11_payload"] == {
        "skills_to_emphasize": [
            "Python"
        ]
    }


def test_service_handles_structured_resume_sections():
    orchestrator = FakeOrchestrator()

    service = RAGOptimizationService(
        config=TestConfig(),
        embedding_provider=TestEmbeddingProvider(),
        orchestrator=orchestrator,
    )

    resume_data = {
        "summary": "AI ML Engineer",
        "skills": [
            "Python",
            "SQL",
            "RAG",
        ],
        "experience": [
            {
                "job_title": "AI Engineer",
                "company": "Example",
                "bullets": [
                    "Built RAG applications"
                ],
            }
        ],
        "projects": [
            {
                "title": "AI Resume Analyzer",
                "bullets": [
                    "Built JD optimization pipeline"
                ],
            }
        ],
        "education": [
            {
                "degree": "B.Tech",
                "institution": "University",
            }
        ],
        "certifications": [
            "Python Certification"
        ],
    }

    service.optimize(
        jd_analysis={
            "required_skills": [
                "Python",
                "RAG",
            ]
        },
        resume_data=resume_data,
    )

    context = (
        orchestrator.received_resume_context
    )

    assert context["summary"] == "AI ML Engineer"
    assert context["skills"] == [
        "Python",
        "SQL",
        "RAG",
    ]
    assert context["experience"][0][
        "job_title"
    ] == "AI Engineer"
    assert context["projects"][0][
        "title"
    ] == "AI Resume Analyzer"
    assert context["education"][0][
        "degree"
    ] == "B.Tech"
    assert context["certifications"] == [
        "Python Certification"
    ]


def test_service_rejects_invalid_resume_data():
    orchestrator = FakeOrchestrator()

    service = RAGOptimizationService(
        config=TestConfig(),
        embedding_provider=TestEmbeddingProvider(),
        orchestrator=orchestrator,
    )

    try:
        service.optimize(
            jd_analysis={
                "required_skills": ["Python"]
            },
            resume_data="invalid",
        )
    except TypeError as exc:
        assert "resume_data" in str(exc)
    else:
        raise AssertionError(
            "Expected TypeError."
        )


def test_disabled_service_does_not_require_resume_context():
    config = RAGConfig()

    config.enabled = False

    service = RAGOptimizationService(
        config=config
    )

    result = service.optimize(
        jd_analysis={
            "required_skills": ["Python"]
        },
        resume_data={
            "skills": ["Python"]
        },
    )

    assert result["metadata"][
        "rag_enabled"
    ] is False
    assert result["phase11_payload"] == {
        "skills_to_emphasize": [],
        "experience_to_emphasize": [],
        "keywords_to_emphasize": [],
        "emphasis_instructions": [],
        "grounding": [],
        "metadata": {
            "rag_enabled": False,
        },
    }