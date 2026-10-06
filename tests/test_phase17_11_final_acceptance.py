import io
from pathlib import Path

import pytest
from docx import Document
from flask import Flask
from pypdf import PdfReader

from app import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def resume_pdf():
    return (
        b"%PDF-1.4\n"
        b"1 0 obj\n"
        b"<< /Type /Catalog /Pages 2 0 R >>\n"
        b"endobj\n"
        b"2 0 obj\n"
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>\n"
        b"endobj\n"
        b"3 0 obj\n"
        b"<< /Type /Page /Parent 2 0 R "
        b"/MediaBox [0 0 612 792] "
        b"/Contents 4 0 R >>\n"
        b"endobj\n"
        b"4 0 obj\n"
        b"<< /Length 44 >>\n"
        b"stream\n"
        b"BT /F1 12 Tf 72 720 Td "
        b"(Python Developer Resume) Tj ET\n"
        b"endstream\n"
        b"endobj\n"
        b"xref\n"
        b"0 5\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        b"0000000267 00000 n \n"
        b"trailer\n"
        b"<< /Size 5 /Root 1 0 R >>\n"
        b"startxref\n"
        b"359\n"
        b"%%EOF"
    )


def test_final_acceptance_app_starts(client):
    response = client.get("/")

    assert response.status_code in {200, 404}


def test_final_acceptance_resume_upload(client, resume_pdf):
    response = client.post(
        "/api/resume/upload",
        data={
            "resume": (
                io.BytesIO(resume_pdf),
                "acceptance_resume.pdf",
            )
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["filename"]
    assert "text" in data


def test_final_acceptance_job_description(client):
    response = client.post(
        "/api/job-description",
        json={
            "job_description": (
                "Python Developer with Python, Flask, SQL, "
                "REST APIs, machine learning and Git experience."
            )
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, dict)


def test_final_acceptance_generation_validation(client):
    response = client.post(
        "/api/resume/generate",
        json={
            "resume_text": "",
            "job_description": "Python Developer",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data is not None


def test_final_acceptance_rewrite_validation(client):
    response = client.post(
        "/api/resume/rewrite",
        json={},
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data is not None


def test_final_acceptance_download_validation(client):
    response = client.get("/api/resume/download")

    assert response.status_code == 400

    data = response.get_json()

    assert data is not None


def test_final_acceptance_invalid_download_extension(client):
    response = client.get(
        "/api/resume/download?filename=optimized_resume.exe"
    )

    assert response.status_code in {400, 404}

    data = response.get_json()

    assert data is not None


def test_final_acceptance_unknown_template(client):
    response = client.post(
        "/api/resume/generate",
        json={
            "resume_text": "Python Developer with Python and SQL experience.",
            "job_description": "Python Developer",
            "template": "nonexistent_template",
        },
    )

    assert response.status_code in {400, 500}

    data = response.get_json()

    assert data is not None