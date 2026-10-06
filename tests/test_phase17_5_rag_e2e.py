from pathlib import Path

from app import create_app
from app.rag.config import RAGConfig
from app.rag.optimization.service import RAGOptimizationService


def create_test_app():
    app = create_app()
    app.config["TESTING"] = True
    return app


def sample_resume_text():
    return """
    Alex Johnson
    alex@example.com
    AI/ML Engineer

    AI/ML Engineer with experience in Python,
    Machine Learning, SQL, Generative AI and RAG.

    Skills
    Python, Machine Learning, SQL, Generative AI, RAG, Pandas

    Experience
    AI/ML Engineer - Example Technologies - 2024-2025
    Built machine learning and Generative AI applications
    using Python, SQL and retrieval-augmented generation.

    Projects
    AI Resume Analyzer
    Built a resume and job-description matching platform
    using Python and RAG.

    Education
    B.Tech - Example University - 2024
    """


def sample_resume_data():
    return {
        "personal_info": {
            "name": "Alex Johnson",
            "email": "alex@example.com",
        },
        "summary": (
            "AI/ML Engineer with experience in Python, "
            "Machine Learning, SQL, Generative AI and RAG."
        ),
        "skills": [
            "Python",
            "Machine Learning",
            "SQL",
            "Generative AI",
            "RAG",
            "Pandas",
        ],
        "experience": [
            {
                "job_title": "AI/ML Engineer",
                "company": "Example Technologies",
                "dates": "2024-2025",
                "description": (
                    "Built machine learning and Generative AI "
                    "applications using Python and RAG."
                ),
            }
        ],
        "projects": [
            {
                "name": "AI Resume Analyzer",
                "description": (
                    "Built a resume and job-description "
                    "matching platform using Python and RAG."
                ),
            }
        ],
        "education": [
            {
                "degree": "B.Tech",
                "institution": "Example University",
                "year": "2024",
            }
        ],
        "certifications": [],
    }


def sample_job_description():
    return """
    We are looking for an AI/ML Engineer with experience in
    Python, Machine Learning, SQL, Generative AI and RAG.

    The candidate should build production-ready AI applications,
    work with retrieval-augmented generation workflows,
    and develop Python-based solutions.
    """


def test_rag_service_can_be_enabled():
    config = RAGConfig()
    config.enabled = True

    service = RAGOptimizationService(
        config=config,
    )

    assert service is not None
    assert service.config.enabled is True


def test_rag_service_can_be_disabled():
    config = RAGConfig()
    config.enabled = False

    service = RAGOptimizationService(
        config=config,
    )

    assert service is not None
    assert service.config.enabled is False


def test_rag_disabled_does_not_break_optimization():
    config = RAGConfig()
    config.enabled = False

    service = RAGOptimizationService(
        config=config,
    )

    result = service.optimize(
        {
            "cleaned_text": sample_job_description(),
            "required_skills": [
                "Python",
                "Machine Learning",
            ],
            "qualifications": [],
            "experience": [],
            "keywords": [
                "Python",
                "machine learning",
            ],
        },
        resume_data=sample_resume_data(),
    )

    assert isinstance(result, dict)

    assert result.get("enabled") is False


def test_rag_enabled_returns_optimization_result():
    config = RAGConfig()
    config.enabled = True

    service = RAGOptimizationService(
        config=config,
    )

    result = service.optimize(
        {
            "cleaned_text": sample_job_description(),
            "required_skills": [
                "Python",
                "Machine Learning",
                "Generative AI",
                "RAG",
            ],
            "qualifications": [],
            "experience": [],
            "keywords": [
                "Python",
                "machine learning",
                "Generative AI",
                "RAG",
            ],
        },
        resume_data=sample_resume_data(),
    )

    assert isinstance(result, dict)
    assert result.get("enabled") is True

    assert "phase11_payload" in result
    assert isinstance(
        result["phase11_payload"],
        dict,
    )


def test_generation_endpoint_runs_with_rag_enabled():
    app = create_test_app()

    with app.test_client() as client:
        response = client.post(
            "/api/resume/generate",
            json={
                "resume_text": sample_resume_text(),
                "resume_data": sample_resume_data(),
                "job_description": sample_job_description(),
                "target_pages": 1,
                "template": "ats_clean",
            },
        )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"

    assert "final_resume" in data
    assert "validation" in data
    assert "document_path" in data
    assert "pdf_path" in data

    assert Path(data["document_path"]).is_file()
    assert Path(data["pdf_path"]).is_file()


def test_rag_generation_does_not_leak_internal_metadata():
    app = create_test_app()

    with app.test_client() as client:
        response = client.post(
            "/api/resume/generate",
            json={
                "resume_text": sample_resume_text(),
                "resume_data": sample_resume_data(),
                "job_description": sample_job_description(),
                "target_pages": 1,
                "template": "ats_clean",
            },
        )

    assert response.status_code == 200

    data = response.get_json()

    final_resume = str(
        data["final_resume"]
    ).lower()

    assert "knowledge_context" not in final_resume
    assert "source_chunk_id" not in final_resume
    assert "evidence_id" not in final_resume
    assert "rag_optimization" not in final_resume