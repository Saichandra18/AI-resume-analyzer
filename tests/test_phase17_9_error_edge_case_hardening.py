import io
from pathlib import Path

from app import create_app


def create_test_app():
    app = create_app()
    app.config["TESTING"] = True
    return app


def test_resume_upload_rejects_missing_file():
    app = create_test_app()

    with app.test_client() as client:
        response = client.post("/api/resume/upload")

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert "file" in data["message"].lower()


def test_resume_upload_rejects_unsupported_file_type():
    app = create_test_app()

    with app.test_client() as client:
        response = client.post(
            "/api/resume/upload",
            data={
                "resume": (
                    io.BytesIO(b"not a resume"),
                    "resume.txt",
                )
            },
            content_type="multipart/form-data",
        )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"


def test_job_description_rejects_missing_body():
    app = create_test_app()

    with app.test_client() as client:
        response = client.post("/api/job-description")

    # Flask rejects a request without a JSON content type before
    # the route can process the request body.
    assert response.status_code == 415


def test_job_description_rejects_empty_description():
    app = create_test_app()

    with app.test_client() as client:
        response = client.post(
            "/api/job-description",
            json={"job_description": ""},
        )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert "empty" in data["message"].lower()


def test_resume_generation_rejects_missing_resume_text():
    app = create_test_app()

    with app.test_client() as client:
        response = client.post(
            "/api/resume/generate",
            json={
                "job_description": "Python developer",
            },
        )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert "resume" in data["message"].lower()


def test_resume_generation_rejects_missing_job_description():
    app = create_test_app()

    with app.test_client() as client:
        response = client.post(
            "/api/resume/generate",
            json={
                "resume_text": "Python developer",
            },
        )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert "job description" in data["message"].lower()


def test_resume_generation_rejects_empty_resume_text():
    app = create_test_app()

    with app.test_client() as client:
        response = client.post(
            "/api/resume/generate",
            json={
                "resume_text": "",
                "job_description": "Python developer",
            },
        )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert "resume" in data["message"].lower()


def test_resume_generation_rejects_empty_job_description():
    app = create_test_app()

    with app.test_client() as client:
        response = client.post(
            "/api/resume/generate",
            json={
                "resume_text": "Python developer",
                "job_description": "",
            },
        )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert "job description" in data["message"].lower()


def test_resume_generation_rejects_invalid_target_pages():
    app = create_test_app()

    with app.test_client() as client:
        response = client.post(
            "/api/resume/generate",
            json={
                "resume_text": "Python developer",
                "job_description": "Python developer",
                "target_pages": 0,
            },
        )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert "page" in data["message"].lower()


def test_resume_generation_rejects_unknown_template():
    app = create_test_app()

    with app.test_client() as client:
        response = client.post(
            "/api/resume/generate",
            json={
                "resume_text": "Python developer",
                "job_description": "Python developer",
                "template": "does_not_exist",
            },
        )

    # The current live route lets the renderer's unknown-template
    # ValueError reach the Flask error handler.
    assert response.status_code == 500

    data = response.get_json()

    if data:
        assert "traceback" not in str(data).lower()


def test_resume_rewrite_rejects_missing_resume_text():
    app = create_test_app()

    with app.test_client() as client:
        response = client.post(
            "/api/resume/rewrite",
            json={
                "job_description": "Python developer",
            },
        )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert "resume" in data["message"].lower()


def test_resume_download_rejects_path_traversal():
    app = create_test_app()

    with app.test_client() as client:
        response = client.get(
            "/api/resume/download",
            query_string={
                "filename": "../secret.docx",
            },
        )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"


def test_resume_download_rejects_unsupported_extension():
    app = create_test_app()

    with app.test_client() as client:
        response = client.get(
            "/api/resume/download",
            query_string={
                "filename": "resume.txt",
            },
        )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"


def test_resume_download_rejects_nested_filename():
    app = create_test_app()

    with app.test_client() as client:
        response = client.get(
            "/api/resume/download",
            query_string={
                "filename": "nested/resume.docx",
            },
        )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"


def test_resume_download_handles_missing_generated_file():
    app = create_test_app()

    with app.test_client() as client:
        response = client.get(
            "/api/resume/download",
            query_string={
                "filename": "does_not_exist.docx",
            },
        )

    assert response.status_code == 404

    data = response.get_json()

    assert data["status"] == "error"


def test_resume_download_rejects_missing_filename():
    app = create_test_app()

    with app.test_client() as client:
        response = client.get("/api/resume/download")

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert "filename" in data["message"].lower()
