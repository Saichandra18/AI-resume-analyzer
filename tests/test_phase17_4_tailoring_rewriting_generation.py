from pathlib import Path

from app import create_app
from app.resume_generation_service import (
    generate_optimized_resume_documents,
)


def create_test_app():
    app = create_app()
    app.config["TESTING"] = True
    return app


def sample_resume_text():
    return """
    Alex Johnson
    alex@example.com
    +91-9876543210
    India

    AI/ML Engineer

    AI/ML Engineer with experience building machine learning
    and Generative AI applications.

    Skills
    Python, Machine Learning, SQL, Pandas, Flask, Generative AI, RAG

    Experience
    AI/ML Engineer - Example Technologies - 2024-2025
    Built machine learning and Generative AI applications
    using Python, SQL and RAG.

    Projects
    AI Resume Analyzer
    Built a resume and job-description matching platform
    using Python, Flask, SQL and RAG.

    Education
    B.Tech - Example University - 2024
    """


def sample_resume_data():
    return {
        "personal_info": {
            "name": "Alex Johnson",
            "email": "alex@example.com",
            "phone": "+91-9876543210",
            "location": "India",
        },
        "skills": [
            "Python",
            "Machine Learning",
            "SQL",
            "Pandas",
            "Flask",
            "Generative AI",
            "RAG",
        ],
        "education": [
            {
                "degree": "B.Tech",
                "institution": "Example University",
                "year": "2024",
            }
        ],
        "experience": [
            {
                "job_title": "AI/ML Engineer",
                "company": "Example Technologies",
                "dates": "2024-2025",
                "location": "India",
                "description": (
                    "Built machine learning and Generative AI "
                    "applications using Python, SQL and RAG."
                ),
            }
        ],
        "projects": [
            {
                "name": "AI Resume Analyzer",
                "description": (
                    "Built a resume and job-description matching "
                    "platform using Python, Flask, SQL and RAG."
                ),
            }
        ],
        "certifications": [],
    }


def sample_job_description():
    return """
    We are looking for an AI/ML Engineer with experience in
    Python, machine learning, SQL, Generative AI and RAG.

    Responsibilities include building production-ready AI
    applications, developing retrieval-augmented generation
    workflows, working with structured data and creating
    scalable Python applications.

    Experience with Docker, AWS and Kubernetes is preferred.
    """


def test_rewrite_endpoint_accepts_tailoring_context():
    app = create_test_app()

    payload = {
        "resume_text": sample_resume_text(),
        "resume_data": sample_resume_data(),
        "tailoring_plan": {
            "target_role": "AI/ML Engineer",
            "prioritize": [
                "Python",
                "Machine Learning",
                "Generative AI",
                "RAG",
            ],
        },
        "job_description": sample_job_description(),
        "experience": sample_resume_data()["experience"],
        "projects": sample_resume_data()["projects"],
        "skills": sample_resume_data()["skills"],
    }

    with app.test_client() as client:
        response = client.post(
            "/api/resume/rewrite",
            json=payload,
        )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert "rewrite" in data
    assert data["rewrite"] is not None


def test_rewrite_endpoint_requires_resume_text():
    app = create_test_app()

    payload = {
        "resume_data": sample_resume_data(),
        "tailoring_plan": {},
        "job_description": sample_job_description(),
    }

    with app.test_client() as client:
        response = client.post(
            "/api/resume/rewrite",
            json=payload,
        )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert "resume text" in data["message"].lower()


def test_generation_accepts_tailoring_plan():
    app = create_test_app()

    payload = {
        "resume_text": sample_resume_text(),
        "resume_data": sample_resume_data(),
        "job_description": sample_job_description(),
        "tailoring_plan": {
            "target_role": "AI/ML Engineer",
            "prioritize": [
                "Python",
                "Machine Learning",
                "Generative AI",
                "RAG",
            ],
        },
        "target_pages": 1,
        "template": "ats_clean",
    }

    with app.test_client() as client:
        response = client.post(
            "/api/resume/generate",
            json=payload,
        )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert "final_resume" in data
    assert "validation" in data
    assert "document_path" in data
    assert "pdf_path" in data


def test_complete_tailoring_rewriting_generation_flow(tmp_path):
    resume_text = sample_resume_text()
    resume_data = sample_resume_data()
    job_description = sample_job_description()

    tailoring_plan = {
        "target_role": "AI/ML Engineer",
        "prioritize": [
            "Python",
            "Machine Learning",
            "Generative AI",
            "RAG",
            "SQL",
        ],
    }

    docx_path = tmp_path / "optimized_resume.docx"
    pdf_path = tmp_path / "optimized_resume.pdf"

    result = generate_optimized_resume_documents(
        resume_text=resume_text,
        docx_output_path=docx_path,
        pdf_output_path=pdf_path,
        resume_data=resume_data,
        job_description=job_description,
        tailoring_plan=tailoring_plan,
        target_pages=1,
        template="ats_clean",
    )

    assert isinstance(result, dict)

    assert "final_resume" in result
    assert "validation" in result

    assert Path(result["document_path"]).is_file()
    assert Path(result["pdf_path"]).is_file()

    final_resume = result["final_resume"]

    assert final_resume is not None

    if hasattr(final_resume, "to_dict"):
        final_resume_data = final_resume.to_dict()

        assert isinstance(final_resume_data, dict)
        assert final_resume_data


def test_generation_produces_job_optimized_content(tmp_path):
    resume_data = sample_resume_data()

    result = generate_optimized_resume_documents(
        resume_text=sample_resume_text(),
        docx_output_path=tmp_path / "optimized.docx",
        pdf_output_path=tmp_path / "optimized.pdf",
        resume_data=resume_data,
        job_description=sample_job_description(),
        tailoring_plan={
            "target_role": "AI/ML Engineer",
            "prioritize": [
                "Python",
                "Machine Learning",
                "Generative AI",
                "RAG",
            ],
        },
        target_pages=1,
        template="ats_clean",
    )

    assert result["final_resume"] is not None

    final_resume = result["final_resume"]

    if hasattr(final_resume, "to_dict"):
        final_data = final_resume.to_dict()

        searchable_text = str(final_data).lower()

        assert (
            "python" in searchable_text
            or "machine learning" in searchable_text
            or "generative ai" in searchable_text
        )


def test_original_resume_text_is_not_mutated(tmp_path):
    original_text = sample_resume_text()

    generate_optimized_resume_documents(
        resume_text=original_text,
        docx_output_path=tmp_path / "optimized.docx",
        pdf_output_path=tmp_path / "optimized.pdf",
        resume_data=sample_resume_data(),
        job_description=sample_job_description(),
        tailoring_plan={
            "target_role": "AI/ML Engineer",
            "prioritize": [
                "Python",
                "Machine Learning",
                "Generative AI",
                "RAG",
            ],
        },
        target_pages=1,
        template="ats_clean",
    )

    assert original_text == sample_resume_text()