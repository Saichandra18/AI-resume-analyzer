from copy import deepcopy
from pathlib import Path

import pytest
from docx import Document
from pypdf import PdfReader

from app import create_app
from app.resume_generation_service import (
    generate_optimized_resume_documents,
)


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_resume_data():
    return {
        "personal_info": {
            "name": "Alex Johnson",
            "email": "alex@example.com",
            "phone": "+91-9876543210",
            "location": "India",
        },
        "summary": (
            "AI/ML Engineer with experience in Python, "
            "machine learning, SQL, and Generative AI."
        ),
        "skills": [
            "Python",
            "Machine Learning",
            "SQL",
            "Generative AI",
            "RAG",
            "Prompt Engineering",
        ],
        "experience": [
            {
                "job_title": "AI/ML Engineer",
                "company": "Example Technologies",
                "dates": "2024 – 2025",
                "location": "India",
                "bullets": [
                    "Developed machine learning solutions using Python.",
                    "Built Generative AI and RAG workflows.",
                    "Worked with SQL-based data processing.",
                ],
            }
        ],
        "projects": [
            {
                "title": "Generative AI Resume Analyzer",
                "bullets": [
                    "Built a Generative AI application using RAG.",
                    "Implemented resume and job-description matching.",
                ],
                "technologies": [
                    "Python",
                    "RAG",
                    "Generative AI",
                ],
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


@pytest.fixture
def sample_resume_text():
    return """
    Alex Johnson
    alex@example.com
    +91-9876543210
    India

    AI/ML Engineer

    AI/ML Engineer with experience in Python, machine learning,
    SQL, Generative AI, RAG, and prompt engineering.

    Skills
    Python
    Machine Learning
    SQL
    Generative AI
    RAG
    Prompt Engineering

    Experience
    AI/ML Engineer – Example Technologies
    2024 – 2025
    India
    Developed machine learning solutions using Python.
    Built Generative AI and RAG workflows.
    Worked with SQL-based data processing.

    Projects
    Generative AI Resume Analyzer
    Built a Generative AI application using RAG.
    Implemented resume and job-description matching.

    Education
    B.Tech – Example University
    2024
    """.strip()


@pytest.fixture
def sample_job_description():
    return """
    We are looking for an AI/ML Engineer with experience in
    Python, machine learning, SQL, Generative AI, RAG,
    prompt engineering, and natural language processing.

    Responsibilities include building machine learning systems,
    developing Generative AI applications, implementing
    retrieval-augmented generation workflows, and working
    with structured data.
    """.strip()


def test_complete_resume_to_generation_flow(
    tmp_path,
    sample_resume_text,
    sample_resume_data,
    sample_job_description,
):
    """
    Validate the complete generation service journey:

    resume + JD
        -> tailoring
        -> JD targeting
        -> RAG
        -> rewriting
        -> selection
        -> prioritization
        -> length control
        -> FinalResume
        -> validation
        -> DOCX + PDF
        -> ATS evaluation
        -> document validation
    """

    original_resume_data = deepcopy(sample_resume_data)

    docx_path = tmp_path / "optimized_resume.docx"
    pdf_path = tmp_path / "optimized_resume.pdf"

    result = generate_optimized_resume_documents(
        resume_text=sample_resume_text,
        docx_output_path=docx_path,
        pdf_output_path=pdf_path,
        resume_data=sample_resume_data,
        job_description=sample_job_description,
        target_pages=1,
        target_job_title="AI/ML Engineer",
        experience_level="experienced",
        template="ats_clean",
    )

    assert result["final_resume"] is not None

    assert result["validation"]["valid"] is True

    assert result["document_path"]
    assert result["pdf_path"]

    assert Path(result["document_path"]).is_file()
    assert Path(result["pdf_path"]).is_file()

    assert result["ats_evaluation"] is not None
    assert result["document_validation"] is not None

    # Generation must not mutate caller-owned resume data.
    assert sample_resume_data == original_resume_data

    # Generated DOCX must contain extractable content.
    document = Document(result["document_path"])

    docx_text = "\n".join(
        paragraph.text
        for paragraph in document.paragraphs
    )

    assert docx_text.strip()

    # Generated PDF must contain extractable content.
    reader = PdfReader(result["pdf_path"])

    assert len(reader.pages) >= 1

    pdf_text = "\n".join(
        page.extract_text() or ""
        for page in reader.pages
    )

    assert pdf_text.strip()


def test_complete_resume_to_ats_validation_flow(
    tmp_path,
    sample_resume_text,
    sample_resume_data,
    sample_job_description,
):
    """
    Validate that generation produces the information required
    for downstream ATS comparison and final validation.
    """

    result = generate_optimized_resume_documents(
        resume_text=sample_resume_text,
        docx_output_path=tmp_path / "resume.docx",
        pdf_output_path=tmp_path / "resume.pdf",
        resume_data=sample_resume_data,
        job_description=sample_job_description,
        target_pages=1,
        template="ats_clean",
    )

    assert result["validation"]["valid"] is True

    ats_evaluation = result["ats_evaluation"]

    assert isinstance(ats_evaluation, dict)
    assert "comparison" in ats_evaluation

    document_validation = result["document_validation"]

    assert isinstance(document_validation, dict)


def test_complete_jd_to_optimized_resume_flow(
    tmp_path,
    sample_resume_text,
    sample_resume_data,
    sample_job_description,
):
    """
    Validate JD-driven optimization without manually supplying
    an ATS target payload.
    """

    result = generate_optimized_resume_documents(
        resume_text=sample_resume_text,
        docx_output_path=tmp_path / "jd_optimized.docx",
        pdf_output_path=tmp_path / "jd_optimized.pdf",
        resume_data=sample_resume_data,
        job_description=sample_job_description,
        target_job_title="AI/ML Engineer",
        template="ats_clean",
    )

    final_resume = result["final_resume"]

    assert final_resume is not None
    assert result["validation"]["valid"] is True

    assert Path(result["document_path"]).exists()
    assert Path(result["pdf_path"]).exists()

    # The generated resume should retain candidate-supported
    # target terminology.
    final_resume_dict = final_resume.to_dict()

    combined_text = str(final_resume_dict).lower()

    assert "python" in combined_text
    assert "generative ai" in combined_text


def test_complete_rag_aware_generation_flow(
    tmp_path,
    sample_resume_text,
    sample_resume_data,
    sample_job_description,
):
    """
    Validate the generation pipeline with an explicit RAG service.

    The test intentionally uses the existing RAG service contract
    rather than mocking the entire optimization pipeline.
    """

    from app.rag.config import RAGConfig
    from app.rag.optimization.service import (
        RAGOptimizationService,
    )

    config = RAGConfig()
    config.enabled = True

    rag_service = RAGOptimizationService(
        config=config,
    )

    result = generate_optimized_resume_documents(
        resume_text=sample_resume_text,
        docx_output_path=tmp_path / "rag_resume.docx",
        pdf_output_path=tmp_path / "rag_resume.pdf",
        resume_data=sample_resume_data,
        job_description=sample_job_description,
        target_pages=1,
        target_job_title="AI/ML Engineer",
        template="ats_clean",
        rag_service=rag_service,
    )

    assert result["final_resume"] is not None
    assert result["validation"]["valid"] is True

    assert Path(result["document_path"]).exists()
    assert Path(result["pdf_path"]).exists()

    assert "rag_optimization" in result


def test_complete_multi_format_generation_flow(
    tmp_path,
    sample_resume_text,
    sample_resume_data,
    sample_job_description,
):
    """
    DOCX and PDF must be produced from the same successful
    optimization run.
    """

    result = generate_optimized_resume_documents(
        resume_text=sample_resume_text,
        docx_output_path=tmp_path / "resume.docx",
        pdf_output_path=tmp_path / "resume.pdf",
        resume_data=sample_resume_data,
        job_description=sample_job_description,
        template="ats_clean",
    )

    assert Path(result["document_path"]).suffix == ".docx"
    assert Path(result["pdf_path"]).suffix == ".pdf"

    assert Path(result["document_path"]).stat().st_size > 0
    assert Path(result["pdf_path"]).stat().st_size > 0

    assert result["validation"]["valid"] is True
    assert result["document_validation"] is not None


def test_complete_template_switching_flow(
    tmp_path,
    sample_resume_text,
    sample_resume_data,
    sample_job_description,
):
    """
    Validate that the complete generation pipeline accepts
    multiple professional templates.
    """

    templates = [
        "default",
        "ats_clean",
        "modern_professional",
        "compact_technical",
    ]

    for template in templates:
        result = generate_optimized_resume_documents(
            resume_text=sample_resume_text,
            docx_output_path=(
                tmp_path / f"{template}.docx"
            ),
            pdf_output_path=(
                tmp_path / f"{template}.pdf"
            ),
            resume_data=sample_resume_data,
            job_description=sample_job_description,
            template=template,
        )

        assert result["validation"]["valid"] is True

        assert Path(
            result["document_path"]
        ).exists()

        assert Path(
            result["pdf_path"]
        ).exists()


def test_complete_pipeline_preserves_original_resume(
    tmp_path,
    sample_resume_text,
    sample_resume_data,
    sample_job_description,
):
    """
    Verify the full generation pipeline respects its
    non-mutation contract.
    """

    original = deepcopy(sample_resume_data)

    generate_optimized_resume_documents(
        resume_text=sample_resume_text,
        docx_output_path=tmp_path / "resume.docx",
        pdf_output_path=tmp_path / "resume.pdf",
        resume_data=sample_resume_data,
        job_description=sample_job_description,
        template="ats_clean",
    )

    assert sample_resume_data == original


def test_generation_api_requires_resume_and_job_description(
    client,
):
    response = client.post(
        "/api/resume/generate",
        json={},
    )

    assert response.status_code == 400

    payload = response.get_json()

    assert payload["status"] == "error"
    assert "Resume text is required" in payload["message"]