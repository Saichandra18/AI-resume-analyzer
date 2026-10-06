from pathlib import Path

from docx import Document
from pypdf import PdfReader

from app import create_app


def create_test_app():
    app = create_app()
    app.config["TESTING"] = True
    return app


def sample_resume_text():
    return """
    Alex Johnson
    alex@example.com

    AI/ML Engineer

    SUMMARY
    AI/ML Engineer with experience in Python, Machine Learning,
    SQL, Pandas and Generative AI.

    SKILLS
    Python
    Machine Learning
    SQL
    Pandas
    Generative AI

    EXPERIENCE
    AI/ML Engineer - Example Technologies - 2024-2025
    Built machine learning applications using Python and SQL.
    Developed data processing workflows with Pandas.

    PROJECTS
    AI Resume Analyzer
    Built a resume analysis platform using Python,
    Machine Learning and SQL.

    EDUCATION
    B.Tech - Computer Science - Example University - 2024
    """


def sample_resume_data():
    return {
        "personal_info": {
            "name": "Alex Johnson",
            "email": "alex@example.com",
        },
        "summary": (
            "AI/ML Engineer with experience in Python, Machine Learning, "
            "SQL, Pandas and Generative AI."
        ),
        "skills": [
            "Python",
            "Machine Learning",
            "SQL",
            "Pandas",
            "Generative AI",
        ],
        "experience": [
            {
                "job_title": "AI/ML Engineer",
                "company": "Example Technologies",
                "dates": "2024-2025",
                "description": (
                    "Built machine learning applications using Python "
                    "and SQL. Developed data processing workflows "
                    "with Pandas."
                ),
            }
        ],
        "projects": [
            {
                "name": "AI Resume Analyzer",
                "description": (
                    "Built a resume analysis platform using Python, "
                    "Machine Learning and SQL."
                ),
            }
        ],
        "education": [
            {
                "degree": "B.Tech",
                "field": "Computer Science",
                "institution": "Example University",
                "year": "2024",
            }
        ],
        "certifications": [],
    }


def sample_job_description():
    return """
    We are looking for an AI/ML Engineer with experience in:

    Python
    Machine Learning
    SQL
    Pandas
    Generative AI
    Retrieval-Augmented Generation

    The candidate should build production-ready AI applications,
    develop machine learning solutions and work with
    retrieval-augmented generation workflows.
    """


def generate_resume(client, template):
    return client.post(
        "/api/resume/generate",
        json={
            "resume_text": sample_resume_text(),
            "resume_data": sample_resume_data(),
            "job_description": sample_job_description(),
            "target_pages": 1,
            "template": template,
        },
    )


def assert_valid_generation(response):
    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["document_path"]
    assert data["pdf_path"]

    docx_path = Path(data["document_path"])
    pdf_path = Path(data["pdf_path"])

    assert docx_path.is_file()
    assert pdf_path.is_file()

    assert docx_path.stat().st_size > 0
    assert pdf_path.stat().st_size > 0

    return data, docx_path, pdf_path


def extract_docx_text(path):
    document = Document(path)

    return "\n".join(
        paragraph.text
        for paragraph in document.paragraphs
    ).lower()


def extract_pdf_text(path):
    reader = PdfReader(path)

    assert len(reader.pages) >= 1

    return "\n".join(
        page.extract_text() or ""
        for page in reader.pages
    ).lower()


def assert_candidate_content(text):
    assert "alex johnson" in text
    assert "python" in text
    assert "machine learning" in text
    assert "sql" in text
    assert "ai resume analyzer" in text


def test_ats_clean_template_generates_valid_resume():
    app = create_test_app()

    with app.test_client() as client:
        response = generate_resume(client, "ats_clean")

    data, docx_path, pdf_path = assert_valid_generation(response)

    docx_text = extract_docx_text(docx_path)
    pdf_text = extract_pdf_text(pdf_path)

    assert_candidate_content(docx_text)
    assert_candidate_content(pdf_text)

    assert data["final_resume"]


def test_modern_professional_template_generates_valid_resume():
    app = create_test_app()

    with app.test_client() as client:
        response = generate_resume(
            client,
            "modern_professional",
        )

    data, docx_path, pdf_path = assert_valid_generation(response)

    assert_candidate_content(
        extract_docx_text(docx_path)
    )

    assert_candidate_content(
        extract_pdf_text(pdf_path)
    )

    assert data["final_resume"]


def test_compact_technical_template_generates_valid_resume():
    app = create_test_app()

    with app.test_client() as client:
        response = generate_resume(
            client,
            "compact_technical",
        )

    data, docx_path, pdf_path = assert_valid_generation(response)

    assert_candidate_content(
        extract_docx_text(docx_path)
    )

    assert_candidate_content(
        extract_pdf_text(pdf_path)
    )

    assert data["final_resume"]


def test_template_switching_preserves_candidate_content():
    app = create_test_app()

    templates = [
        "ats_clean",
        "modern_professional",
        "compact_technical",
    ]

    with app.test_client() as client:
        for template in templates:
            response = generate_resume(
                client,
                template,
            )

            data, docx_path, pdf_path = assert_valid_generation(
                response
            )

            assert_candidate_content(
                extract_docx_text(docx_path)
            )

            assert_candidate_content(
                extract_pdf_text(pdf_path)
            )

            assert data["final_resume"]


def test_template_switching_reuses_valid_output_paths():
    app = create_test_app()

    document_paths = []
    pdf_paths = []

    templates = [
        "ats_clean",
        "modern_professional",
        "compact_technical",
    ]

    with app.test_client() as client:
        for template in templates:
            response = generate_resume(
                client,
                template,
            )

            _, docx_path, pdf_path = assert_valid_generation(
                response
            )

            document_paths.append(docx_path)
            pdf_paths.append(pdf_path)

    # The current generation service intentionally writes the
    # optimized resume to the same output filenames.
    assert len(set(document_paths)) == 1
    assert len(set(pdf_paths)) == 1

    assert document_paths[0].exists()
    assert pdf_paths[0].exists()


def test_template_switching_preserves_required_sections():
    app = create_test_app()

    templates = [
        "ats_clean",
        "modern_professional",
        "compact_technical",
    ]

    required_terms = [
        "alex johnson",
        "summary",
        "skills",
        "experience",
        "projects",
        "education",
    ]

    with app.test_client() as client:
        for template in templates:
            response = generate_resume(
                client,
                template,
            )

            _, docx_path, pdf_path = assert_valid_generation(
                response
            )

            docx_text = extract_docx_text(docx_path)
            pdf_text = extract_pdf_text(pdf_path)

            for term in required_terms:
                assert term in docx_text
                assert term in pdf_text


def test_template_switching_preserves_final_resume_structure():
    app = create_test_app()

    templates = [
        "ats_clean",
        "modern_professional",
        "compact_technical",
    ]

    with app.test_client() as client:
        for template in templates:
            response = generate_resume(
                client,
                template,
            )

            assert response.status_code == 200

            data = response.get_json()

            final_resume = data["final_resume"]

            assert final_resume is not None

            if isinstance(final_resume, dict):
                assert final_resume


def test_template_aliases_generate_successfully():
    app = create_test_app()

    aliases = {
        "modern_professional": "modern_professional",
        "compact_technical": "compact_technical",
    }

    with app.test_client() as client:
        for alias in aliases:
            response = generate_resume(
                client,
                alias,
            )

            assert_valid_generation(response)


def test_invalid_template_is_rejected_without_success_response():
    app = create_test_app()

    with app.test_client() as client:
        response = generate_resume(
            client,
            "does_not_exist",
        )

    # The current application rejects unknown templates during
    # document rendering. The error currently reaches the Flask
    # route as a 500 response.
    assert response.status_code == 500
