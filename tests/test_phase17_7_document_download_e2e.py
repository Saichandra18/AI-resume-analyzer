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


def generate_resume(client):
    return client.post(
        "/api/resume/generate",
        json={
            "resume_text": sample_resume_text(),
            "resume_data": sample_resume_data(),
            "job_description": sample_job_description(),
            "target_pages": 1,
            "template": "ats_clean",
        },
    )


def test_generation_returns_docx_and_pdf_paths():
    app = create_test_app()

    with app.test_client() as client:
        response = generate_resume(client)

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["document_path"]
    assert data["pdf_path"]

    assert str(data["document_path"]).lower().endswith(".docx")
    assert str(data["pdf_path"]).lower().endswith(".pdf")


def test_generated_docx_exists_and_is_non_empty():
    app = create_test_app()

    with app.test_client() as client:
        response = generate_resume(client)

    assert response.status_code == 200

    data = response.get_json()

    docx_path = Path(data["document_path"])

    assert docx_path.is_file()
    assert docx_path.stat().st_size > 0


def test_generated_pdf_exists_and_is_non_empty():
    app = create_test_app()

    with app.test_client() as client:
        response = generate_resume(client)

    assert response.status_code == 200

    data = response.get_json()

    pdf_path = Path(data["pdf_path"])

    assert pdf_path.is_file()
    assert pdf_path.stat().st_size > 0


def test_generated_docx_is_readable_and_contains_candidate_content():
    app = create_test_app()

    with app.test_client() as client:
        response = generate_resume(client)

    assert response.status_code == 200

    data = response.get_json()

    document = Document(data["document_path"])

    text = "\n".join(
        paragraph.text
        for paragraph in document.paragraphs
    ).lower()

    assert "alex johnson" in text
    assert "python" in text
    assert "machine learning" in text


def test_generated_pdf_is_readable_and_contains_candidate_content():
    app = create_test_app()

    with app.test_client() as client:
        response = generate_resume(client)

    assert response.status_code == 200

    data = response.get_json()

    reader = PdfReader(data["pdf_path"])

    assert len(reader.pages) >= 1

    text = "\n".join(
        page.extract_text() or ""
        for page in reader.pages
    ).lower()

    assert "alex johnson" in text
    assert "python" in text
    assert "machine learning" in text


def test_docx_download_returns_generated_file():
    app = create_test_app()

    with app.test_client() as client:
        generation_response = generate_resume(client)

        assert generation_response.status_code == 200

        data = generation_response.get_json()

        filename = Path(
            data["document_path"]
        ).name

        download_response = client.get(
            "/api/resume/download",
            query_string={"filename": filename},
        )

    assert download_response.status_code == 200
    assert download_response.data
    assert (
        download_response.headers["Content-Disposition"]
        .startswith("attachment")
    )

    assert filename in (
        download_response.headers["Content-Disposition"]
    )


def test_pdf_download_returns_generated_file():
    app = create_test_app()

    with app.test_client() as client:
        generation_response = generate_resume(client)

        assert generation_response.status_code == 200

        data = generation_response.get_json()

        filename = Path(
            data["pdf_path"]
        ).name

        download_response = client.get(
            "/api/resume/download",
            query_string={"filename": filename},
        )

    assert download_response.status_code == 200
    assert download_response.data

    assert (
        download_response.headers["Content-Disposition"]
        .startswith("attachment")
    )

    assert filename in (
        download_response.headers["Content-Disposition"]
    )

    assert download_response.headers[
        "Content-Type"
    ].startswith("application/pdf")


def test_downloaded_docx_matches_generated_docx():
    app = create_test_app()

    with app.test_client() as client:
        generation_response = generate_resume(client)

        assert generation_response.status_code == 200

        data = generation_response.get_json()

        docx_path = Path(data["document_path"])
        filename = docx_path.name

        download_response = client.get(
            "/api/resume/download",
            query_string={"filename": filename},
        )

    assert download_response.status_code == 200
    assert download_response.data == docx_path.read_bytes()


def test_downloaded_pdf_matches_generated_pdf():
    app = create_test_app()

    with app.test_client() as client:
        generation_response = generate_resume(client)

        assert generation_response.status_code == 200

        data = generation_response.get_json()

        pdf_path = Path(data["pdf_path"])
        filename = pdf_path.name

        download_response = client.get(
            "/api/resume/download",
            query_string={"filename": filename},
        )

    assert download_response.status_code == 200
    assert download_response.data == pdf_path.read_bytes()


def test_docx_and_pdf_are_generated_for_same_resume():
    app = create_test_app()

    with app.test_client() as client:
        response = generate_resume(client)

    assert response.status_code == 200

    data = response.get_json()

    docx_path = Path(data["document_path"])
    pdf_path = Path(data["pdf_path"])

    assert docx_path.exists()
    assert pdf_path.exists()

    assert docx_path.stem == pdf_path.stem


def test_download_rejects_missing_filename():
    app = create_test_app()

    with app.test_client() as client:
        response = client.get(
            "/api/resume/download"
        )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert "filename" in data["message"].lower()