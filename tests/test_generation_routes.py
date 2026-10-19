import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_generation_route_requires_resume_text(client):
    response = client.post(
        "/api/resume/generate",
        json={
            "job_description": "Python developer",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert "resume text" in data["message"].lower()


def test_generation_route_requires_job_description(client):
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


def test_generation_route_rejects_invalid_target_pages(client):
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
    assert "target_pages" in data["message"]


def test_generation_route_rejects_non_integer_target_pages(client):
    response = client.post(
        "/api/resume/generate",
        json={
            "resume_text": "Python developer",
            "job_description": "Python developer",
            "target_pages": "abc",
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert "target_pages" in data["message"]


def test_generation_route_accepts_valid_request(
    client,
    monkeypatch,
    tmp_path,
):
    output_path = tmp_path / "optimized_resume.docx"

    class FakeFinalResume:
        def to_dict(self):
            return {
                "personal_info": {
                    "name": "Test User",
                },
                "summary": "Python developer",
                "skills": ["Python"],
                "experience": [],
                "projects": [],
                "education": [],
                "certifications": [],
                "section_order": [
                    "summary",
                    "skills",
                ],
                "metadata": {
                    "target_pages": 1,
                },
            }

    def fake_generate(**kwargs):
        return {
            "final_resume": FakeFinalResume(),
            "tailoring_plan": {},
            "rewrite_result": {},
            "length_control": {},
            "validation": {
                "valid": True,
                "errors": [],
                "warnings": [],
            },
            "document_path": output_path,
            "pdf_path": tmp_path / "optimized_resume.pdf",
        }

    monkeypatch.setattr(
        "app.routes.generation_routes.generate_optimized_resume_documents",
        fake_generate,
    )

    response = client.post(
        "/api/resume/generate",
        json={
            "resume_text": "Python developer",
            "job_description": "Python developer",
            "target_pages": 1,
            "experience_level": "fresher",
            "target_job_title": "Python Developer",
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert data["document_path"].endswith(
        "optimized_resume.docx"
    )
    assert data["pdf_path"].endswith(
        "optimized_resume.pdf"
    )
    assert data["final_resume"]["summary"] == (
        "Python developer"
    )
    assert data["validation"]["valid"] is True

def test_generation_route_propagates_generation_parameters(
    client,
    monkeypatch,
    tmp_path,
):
    captured = {}

    class FakeFinalResume:
        def to_dict(self):
            return {
                "personal_info": {"name": "Test User"},
                "summary": "Python developer",
                "skills": ["Python"],
                "experience": [],
                "projects": [],
                "education": [],
                "certifications": [],
                "section_order": ["summary", "skills"],
                "metadata": {"target_pages": 2},
            }

    def fake_generate(**kwargs):
        captured.update(kwargs)

        return {
            "final_resume": FakeFinalResume(),
            "tailoring_plan": {},
            "rewrite_result": {},
            "length_control": {},
            "validation": {
                "valid": True,
                "errors": [],
                "warnings": [],
            },
            "document_path": tmp_path / "optimized_resume.docx",
            "pdf_path": tmp_path / "optimized_resume.pdf",
        }

    monkeypatch.setattr(
        "app.routes.generation_routes.generate_optimized_resume_documents",
        fake_generate,
    )

    tailoring_plan = {
        "target_role": "Python Developer",
        "priority_skills": ["Python", "Flask"],
    }

    resume_data = {
        "personal_info": {"name": "Test User"},
        "skills": ["Python", "Flask"],
    }

    response = client.post(
        "/api/resume/generate",
        json={
            "resume_text": "Python Flask developer",
            "resume_data": resume_data,
            "job_description": "Python Flask Developer",
            "tailoring_plan": tailoring_plan,
            "experience_level": "fresher",
            "target_pages": 2,
            "target_job_title": "Python Developer",
        },
    )

    assert response.status_code == 200

    assert captured["resume_text"] == (
        "Python Flask developer"
    )
    assert captured["resume_data"] == resume_data
    assert captured["job_description"] == (
        "Python Flask Developer"
    )
    assert captured["tailoring_plan"] == tailoring_plan
    assert captured["experience_level"] == "fresher"
    assert captured["target_pages"] == 2
    assert captured["target_job_title"] == (
        "Python Developer"
    )


def test_generation_route_propagates_optional_analysis_data(
    client,
    monkeypatch,
    tmp_path,
):
    captured = {}

    class FakeFinalResume:
        def to_dict(self):
            return {
                "personal_info": {"name": "Test User"},
                "summary": "Developer",
                "skills": ["Python"],
                "experience": [],
                "projects": [],
                "education": [],
                "certifications": [],
                "section_order": ["summary", "skills"],
                "metadata": {"target_pages": 1},
            }

    def fake_generate(**kwargs):
        captured.update(kwargs)

        return {
            "final_resume": FakeFinalResume(),
            "tailoring_plan": {},
            "rewrite_result": {},
            "length_control": {},
            "validation": {
                "valid": True,
                "errors": [],
                "warnings": [],
            },
            "document_path": tmp_path / "optimized_resume.docx",
            "pdf_path": tmp_path / "optimized_resume.pdf",
        }

    monkeypatch.setattr(
        "app.routes.generation_routes.generate_optimized_resume_documents",
        fake_generate,
    )

    ats_result = {"match_score": 82}
    resume_quality = {"score": 75}
    content_quality = {"score": 80}
    suggestions = ["Add measurable achievements"]

    response = client.post(
        "/api/resume/generate",
        json={
            "resume_text": "Developer",
            "job_description": "Software Developer",
            "ats_result": ats_result,
            "resume_quality": resume_quality,
            "content_quality": content_quality,
            "improvement_suggestions": suggestions,
        },
    )

    assert response.status_code == 200

    assert captured["ats_result"] == ats_result
    assert captured["resume_quality"] == resume_quality
    assert captured["content_quality"] == content_quality
    assert captured["improvement_suggestions"] == suggestions


def test_generation_route_returns_controlled_error_on_service_failure(
    client,
    monkeypatch,
    caplog,
):
    def fake_generate(**kwargs):
        raise RuntimeError(
            "Generation service failed"
        )

    monkeypatch.setattr(
        "app.routes.generation_routes.generate_optimized_resume_documents",
        fake_generate,
    )

    with caplog.at_level(
        "ERROR",
        logger="app.routes.generation_routes",
    ):
        response = client.post(
            "/api/resume/generate",
            json={
                "resume_text": "Python developer",
                "job_description": "Python developer",
            },
        )

    assert response.status_code == 500

    data = response.get_json()

    assert data["status"] == "error"
    assert (
        data["message"]
        == "Could not generate optimized resume."
    )

    assert "error" not in data

    assert (
        "Failed to generate optimized resume documents."
        in caplog.text
    )

    assert "Generation service failed" in caplog.text

def test_generation_route_uses_default_generation_options(
    client,
    monkeypatch,
    tmp_path,
):
    captured = {}

    class FakeFinalResume:
        def to_dict(self):
            return {
                "personal_info": {"name": "Test User"},
                "summary": "Developer",
                "skills": ["Python"],
                "experience": [],
                "projects": [],
                "education": [],
                "certifications": [],
                "section_order": ["summary", "skills"],
                "metadata": {"target_pages": 1},
            }

    def fake_generate(**kwargs):
        captured.update(kwargs)

        return {
            "final_resume": FakeFinalResume(),
            "tailoring_plan": {},
            "rewrite_result": {},
            "length_control": {},
            "validation": {
                "valid": True,
                "errors": [],
                "warnings": [],
            },
            "document_path": tmp_path / "optimized_resume.docx",
            "pdf_path": tmp_path / "optimized_resume.pdf",
        }

    monkeypatch.setattr(
        "app.routes.generation_routes.generate_optimized_resume_documents",
        fake_generate,
    )

    response = client.post(
        "/api/resume/generate",
        json={
            "resume_text": "Python developer",
            "job_description": "Python developer",
        },
    )

    assert response.status_code == 200

    assert captured["experience_level"] == (
        "experienced"
    )
    assert captured["target_pages"] == 1
    assert captured["target_job_title"] is None
    assert isinstance(captured["resume_data"], dict)
    assert captured["resume_data"]["raw_text"] == "Python developer"
    assert captured["resume_data"]["skills"] == ["Python"]
    assert captured["tailoring_plan"] is None

def test_generation_route_returns_required_response_fields(
    client,
    monkeypatch,
    tmp_path,
):
    class FakeFinalResume:
        def to_dict(self):
            return {
                "personal_info": {"name": "Test User"},
                "summary": "Python developer",
                "skills": ["Python"],
                "experience": [],
                "projects": [],
                "education": [],
                "certifications": [],
                "section_order": ["summary", "skills"],
                "metadata": {"target_pages": 1},
            }

    def fake_generate(**kwargs):
        return {
            "final_resume": FakeFinalResume(),
            "tailoring_plan": {"priority_skills": ["Python"]},
            "rewrite_result": {"summary": "Python developer"},
            "length_control": {"summary": 1},
            "validation": {
                "valid": True,
                "errors": [],
                "warnings": [],
            },
            "document_path": tmp_path / "optimized_resume.docx",
            "pdf_path": tmp_path / "optimized_resume.pdf",
        }

    monkeypatch.setattr(
        "app.routes.generation_routes.generate_optimized_resume_documents",
        fake_generate,
    )

    response = client.post(
        "/api/resume/generate",
        json={
            "resume_text": "Python developer",
            "job_description": "Python developer",
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "success"
    assert "message" in data
    assert "document_path" in data
    assert "final_resume" in data
    assert "validation" in data


def test_generation_route_serializes_final_resume(
    client,
    monkeypatch,
    tmp_path,
):
    class FakeFinalResume:
        def to_dict(self):
            return {
                "personal_info": {
                    "name": "Chandu",
                    "email": "test@example.com",
                },
                "summary": "AI/ML developer",
                "skills": ["Python", "Flask"],
                "experience": [],
                "projects": [
                    {
                        "title": "AI Resume Analyzer",
                    }
                ],
                "education": [],
                "certifications": [],
                "section_order": [
                    "summary",
                    "skills",
                    "projects",
                ],
                "metadata": {
                    "target_pages": 1,
                    "optimization_enabled": True,
                },
            }

    def fake_generate(**kwargs):
        return {
            "final_resume": FakeFinalResume(),
            "tailoring_plan": {},
            "rewrite_result": {},
            "length_control": {},
            "validation": {
                "valid": True,
                "errors": [],
                "warnings": [],
            },
            "document_path": tmp_path / "optimized_resume.docx",
            "pdf_path": tmp_path / "optimized_resume.pdf",
        }

    monkeypatch.setattr(
        "app.routes.generation_routes.generate_optimized_resume_documents",
        fake_generate,
    )

    response = client.post(
        "/api/resume/generate",
        json={
            "resume_text": "AI/ML developer",
            "job_description": "AI/ML developer",
        },
    )

    data = response.get_json()

    final_resume = data["final_resume"]

    assert final_resume["personal_info"]["name"] == "Chandu"
    assert final_resume["summary"] == "AI/ML developer"
    assert final_resume["skills"] == ["Python", "Flask"]
    assert final_resume["projects"][0]["title"] == (
        "AI Resume Analyzer"
    )
    assert final_resume["metadata"]["target_pages"] == 1


def test_generation_route_preserves_validation_result(
    client,
    monkeypatch,
    tmp_path,
):
    class FakeFinalResume:
        def to_dict(self):
            return {
                "personal_info": {"name": "Test User"},
                "summary": "Developer",
                "skills": ["Python"],
                "experience": [],
                "projects": [],
                "education": [],
                "certifications": [],
                "section_order": ["summary", "skills"],
                "metadata": {"target_pages": 1},
            }

    validation = {
        "valid": False,
        "errors": ["Missing required content"],
        "warnings": ["Duplicate skill"],
    }

    def fake_generate(**kwargs):
        return {
            "final_resume": FakeFinalResume(),
            "tailoring_plan": {},
            "rewrite_result": {},
            "length_control": {},
            "validation": validation,
            "document_path": tmp_path / "optimized_resume.docx",
            "pdf_path": tmp_path / "optimized_resume.pdf",
        }

    monkeypatch.setattr(
        "app.routes.generation_routes.generate_optimized_resume_documents",
        fake_generate,
    )

    response = client.post(
        "/api/resume/generate",
        json={
            "resume_text": "Developer",
            "job_description": "Developer",
        },
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["validation"] == validation
    assert data["validation"]["valid"] is False
    assert data["validation"]["errors"] == [
        "Missing required content"
    ]
    assert data["validation"]["warnings"] == [
        "Duplicate skill"
    ]


def test_generation_route_handles_malformed_json(client):
    response = client.post(
        "/api/resume/generate",
        data="this is not valid json",
        content_type="application/json",
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"


def test_generation_route_does_not_expose_traceback(
    client,
    monkeypatch,
):
    def fake_generate(**kwargs):
        raise RuntimeError(
            "database password=SECRET_VALUE"
        )

    monkeypatch.setattr(
        "app.routes.generation_routes.generate_optimized_resume_documents",
        fake_generate,
    )

    response = client.post(
        "/api/resume/generate",
        json={
            "resume_text": "Python developer",
            "job_description": "Python developer",
        },
    )

    assert response.status_code == 500

    data = response.get_json()

    assert data["status"] == "error"
    assert "Traceback" not in str(data)
    assert "File " not in str(data)
def test_download_requires_filename(client):
    response = client.get(
        "/api/resume/download"
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert "filename" in data["message"].lower()


def test_download_returns_404_when_file_missing(client):
    response = client.get(
        "/api/resume/download"
        "?filename=missing_resume.docx"
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["status"] == "error"
    assert "not found" in data["message"].lower()


def test_download_rejects_path_traversal(client):
    response = client.get(
        "/api/resume/download"
        "?filename=../secret.docx"
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert "invalid" in data["message"].lower()


def test_download_rejects_unsupported_file_type(client):
    response = client.get(
        "/api/resume/download"
        "?filename=resume.txt"
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert "invalid" in data["message"].lower()


def test_download_returns_generated_docx(
    client,
    tmp_path,
    monkeypatch,
):
    generated_dir = tmp_path / "generated_resumes"
    generated_dir.mkdir()

    filename = "optimized_resume.docx"
    document = generated_dir / filename

    document.write_bytes(
        b"fake-docx-content"
    )

    monkeypatch.setattr(
        "app.routes.generation_routes.GENERATED_RESUMES_DIR",
        generated_dir,
    )

    response = client.get(
        "/api/resume/download"
        f"?filename={filename}"
    )

    assert response.status_code == 200

    assert response.data == (
        b"fake-docx-content"
    )

    assert (
        response.headers["Content-Disposition"]
        .startswith("attachment")
    )

    assert (
        "optimized_resume.docx"
        in response.headers["Content-Disposition"]
    )

def test_download_returns_generated_pdf(
    client,
    tmp_path,
    monkeypatch,
):
    generated_dir = tmp_path / "generated_resumes"
    generated_dir.mkdir()

    filename = "optimized_resume.pdf"
    document = generated_dir / filename
    document.write_bytes(b"fake-pdf-content")

    monkeypatch.setattr(
        "app.routes.generation_routes.GENERATED_RESUMES_DIR",
        generated_dir,
    )

    response = client.get(
        "/api/resume/download"
        f"?filename={filename}"
    )

    assert response.status_code == 200
    assert response.data == b"fake-pdf-content"
    assert response.headers["Content-Disposition"].startswith(
        "attachment"
    )
    assert "optimized_resume.pdf" in response.headers[
        "Content-Disposition"
    ]
    assert response.headers["Content-Type"].startswith(
        "application/pdf"
    )


def test_generated_document_can_be_downloaded(
    client,
    monkeypatch,
    tmp_path,
):
    generated_dir = tmp_path / "generated_resumes"
    generated_dir.mkdir()

    filename = "optimized_resume.docx"
    document = generated_dir / filename
    document.write_bytes(b"generated-document")

    monkeypatch.setattr(
        "app.routes.generation_routes.GENERATED_RESUMES_DIR",
        generated_dir,
    )

    response = client.get(
        f"/api/resume/download?filename={filename}"
    )

    assert response.status_code == 200
    assert response.data == b"generated-document"


def test_download_uses_generated_resume_directory(
    client,
    monkeypatch,
    tmp_path,
):
    generated_dir = tmp_path / "generated_resumes"
    generated_dir.mkdir()

    filename = "optimized_resume.docx"
    document = generated_dir / filename
    document.write_bytes(b"correct-document")

    outside_file = tmp_path / filename
    outside_file.write_bytes(b"outside-document")

    monkeypatch.setattr(
        "app.routes.generation_routes.GENERATED_RESUMES_DIR",
        generated_dir,
    )

    response = client.get(
        f"/api/resume/download?filename={filename}"
    )

    assert response.status_code == 200
    assert response.data == b"correct-document"


def test_download_rejects_nested_filename(
    client,
):
    response = client.get(
        "/api/resume/download"
        "?filename=subdir/optimized_resume.docx"
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert "invalid" in data["message"].lower()


def test_download_rejects_docx_with_invalid_suffix(
    client,
):
    response = client.get(
        "/api/resume/download"
        "?filename=optimized_resume.docx.exe"
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["status"] == "error"
    assert "invalid" in data["message"].lower()


def test_download_handles_missing_generated_directory(
    client,
    monkeypatch,
    tmp_path,
):
    missing_dir = tmp_path / "does_not_exist"

    monkeypatch.setattr(
        "app.routes.generation_routes.GENERATED_RESUMES_DIR",
        missing_dir,
    )

    response = client.get(
        "/api/resume/download"
        "?filename=optimized_resume.docx"
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["status"] == "error"
    assert "not found" in data["message"].lower()

def test_generation_route_does_not_expose_internal_exception_details(
    client,
    monkeypatch,
):
    def fake_generate(**kwargs):
        raise RuntimeError(
            "C:\\internal\\project\\secret_config.py: API key failure"
        )

    monkeypatch.setattr(
        "app.routes.generation_routes.generate_optimized_resume_documents",
        fake_generate,
    )

    response = client.post(
        "/api/resume/generate",
        json={
            "resume_text": "Python developer",
            "job_description": "Python developer",
        },
    )

    assert response.status_code == 500

    data = response.get_json()

    assert data["status"] == "error"
    assert (
        data["message"]
        == "Could not generate optimized resume."
    )

    assert "error" not in data

    response_text = response.get_data(
        as_text=True
    )

    assert "secret_config.py" not in response_text
    assert "API key failure" not in response_text


def test_generation_route_logs_exception(
    client,
    monkeypatch,
    caplog,
):
    def fake_generate(**kwargs):
        raise RuntimeError(
            "Simulated generation failure"
        )

    monkeypatch.setattr(
        "app.routes.generation_routes.generate_optimized_resume_documents",
        fake_generate,
    )

    with caplog.at_level(
        "ERROR",
        logger="app.routes.generation_routes",
    ):
        response = client.post(
            "/api/resume/generate",
            json={
                "resume_text": "Python developer",
                "job_description": "Python developer",
            },
        )

    assert response.status_code == 500

    assert (
        "Failed to generate optimized resume documents."
        in caplog.text
    )

    assert (
        "Simulated generation failure"
        in caplog.text
    )


def test_generation_route_rebuilds_missing_resume_data(
    client,
    monkeypatch,
    tmp_path,
):
    reconstructed_data = {
        "personal_info": {
            "name": "Test User",
            "email": "test@example.com",
        },
        "skills": ["Python", "SQL"],
        "experience": {
            "section": ["Built Python applications"],
            "job_titles": ["Python Developer"],
            "years": [],
        },
        "projects": ["AI Resume Analyzer"],
        "education": {
            "section": ["Bachelor of Technology"],
            "degrees": ["B.Tech"],
            "years": [],
        },
        "certifications": [],
    }

    captured = {}

    def fake_structure_resume(resume_text):
        captured["resume_text"] = resume_text
        return reconstructed_data

    class FakeFinalResume:
        def to_dict(self):
            return {
                "personal_info": reconstructed_data["personal_info"],
                "summary": "Python developer",
                "skills": reconstructed_data["skills"],
                "experience": reconstructed_data["experience"]["section"],
                "projects": reconstructed_data["projects"],
                "education": reconstructed_data["education"]["section"],
                "certifications": [],
                "section_order": [
                    "summary",
                    "skills",
                    "experience",
                    "projects",
                    "education",
                ],
                "metadata": {"target_pages": 1},
            }

    def fake_generate(**kwargs):
        captured["resume_data"] = kwargs["resume_data"]

        return {
            "final_resume": FakeFinalResume(),
            "tailoring_plan": {},
            "rewrite_result": {},
            "length_control": {},
            "validation": {
                "valid": True,
                "errors": [],
                "warnings": [],
            },
            "document_path": tmp_path / "optimized_resume.docx",
            "pdf_path": tmp_path / "optimized_resume.pdf",
        }

    monkeypatch.setattr(
        "app.routes.generation_routes.structure_resume",
        fake_structure_resume,
    )
    monkeypatch.setattr(
        "app.routes.generation_routes.generate_optimized_resume_documents",
        fake_generate,
    )

    resume_text = (
        "Test User\n"
        "Email: test@example.com\n"
        "Skills: Python, SQL\n"
        "Experience: Built Python applications\n"
        "Projects: AI Resume Analyzer\n"
        "Education: Bachelor of Technology"
    )

    response = client.post(
        "/api/resume/generate",
        json={
            "resume_text": resume_text,
            "resume_data": {},
            "job_description": "Python developer with SQL skills",
            "target_pages": 1,
        },
    )

    assert response.status_code == 200
    assert captured["resume_text"] == resume_text
    assert captured["resume_data"] == reconstructed_data
    assert captured["resume_data"]["skills"] == ["Python", "SQL"]
    assert captured["resume_data"]["projects"] == ["AI Resume Analyzer"]
