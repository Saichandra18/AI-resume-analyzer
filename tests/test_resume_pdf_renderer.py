
from pathlib import Path

import pytest

from app.final_resume_models import FinalResume
from app.resume_pdf_renderer import render_final_resume_pdf


def valid_personal_info():
    """Return the minimum valid personal information."""
    return {
        "name": "Chandu",
        "email": "chandu@example.com",
    }


def test_render_final_resume_pdf_creates_pdf(tmp_path):
    resume = FinalResume(
        personal_info=valid_personal_info(),
        summary="AI/ML Engineer with Python experience.",
        skills=[
            "Python",
            "Machine Learning",
            "SQL",
        ],
    )

    output_path = tmp_path / "resume.pdf"

    result = render_final_resume_pdf(
        resume,
        output_path,
    )

    assert result == output_path
    assert output_path.exists()
    assert output_path.stat().st_size > 0

    assert output_path.read_bytes().startswith(b"%PDF")


def test_render_final_resume_pdf_requires_final_resume(
    tmp_path,
):
    with pytest.raises(TypeError, match="FinalResume"):
        render_final_resume_pdf(
            {"summary": "AI Engineer"},
            tmp_path / "resume.pdf",
        )


def test_render_final_resume_pdf_requires_pdf_extension(
    tmp_path,
):
    resume = FinalResume(
        personal_info=valid_personal_info(),
        summary="AI Engineer",
    )

    with pytest.raises(
        ValueError,
        match=r"\.pdf extension",
    ):
        render_final_resume_pdf(
            resume,
            tmp_path / "resume.docx",
        )


def test_render_final_resume_pdf_rejects_invalid_resume(
    monkeypatch,
    tmp_path,
):
    resume = FinalResume(
        personal_info=valid_personal_info(),
        summary="AI Engineer",
    )

    def fake_validate(_resume):
        return {
            "valid": False,
            "errors": [
                "Invalid resume content.",
                "Missing required information.",
            ],
        }

    monkeypatch.setattr(
        "app.resume_pdf_renderer.validate_final_resume",
        fake_validate,
    )

    with pytest.raises(
        ValueError,
        match="Cannot render invalid resume",
    ):
        render_final_resume_pdf(
            resume,
            tmp_path / "resume.pdf",
        )


def test_render_final_resume_pdf_can_skip_validation(
    monkeypatch,
    tmp_path,
):
    resume = FinalResume(
        summary="AI Engineer",
    )

    def fail_validation(_resume):
        raise AssertionError(
            "Validation should not run when validate=False."
        )

    monkeypatch.setattr(
        "app.resume_pdf_renderer.validate_final_resume",
        fail_validation,
    )

    output_path = tmp_path / "resume.pdf"

    result = render_final_resume_pdf(
        resume,
        output_path,
        validate=False,
    )

    assert result == output_path
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_render_final_resume_pdf_renders_personal_information(
    tmp_path,
):
    resume = FinalResume(
        personal_info={
            "name": "Chandu",
            "email": "chandu@example.com",
            "phone": "9876543210",
            "location": "India",
            "linkedin": "linkedin.com/in/chandu",
            "github": "github.com/chandu",
            "website": "chandu.dev",
        },
        summary="AI/ML Engineer",
    )

    output_path = tmp_path / "resume.pdf"

    render_final_resume_pdf(
        resume,
        output_path,
    )

    content = output_path.read_bytes()

    assert content.startswith(b"%PDF")
    assert len(content) > 500


def test_render_final_resume_pdf_handles_all_sections(
    tmp_path,
):
    resume = FinalResume(
        personal_info=valid_personal_info(),
        summary="AI/ML Engineer specializing in Generative AI.",
        skills=[
            "Python",
            "SQL",
            "Machine Learning",
            "RAG",
        ],
        experience=[
            {
                "job_title": "AI Engineer",
                "company": "Example Company",
                "location": "India",
                "dates": "2025 - Present",
                "bullets": [
                    "Built machine learning pipelines.",
                    "Developed RAG applications.",
                ],
            }
        ],
        projects=[
            {
                "title": "AI Resume Analyzer",
                "description": [
                    "Built an ATS analysis system.",
                    "Implemented resume optimization.",
                ],
            }
        ],
        education=[
            {
                "degree": "B.Tech",
                "institution": "Example University",
                "year": "2025",
            }
        ],
        certifications=[
            {
                "name": "Python Certification",
                "organization": "Example Institute",
                "year": "2025",
            }
        ],
    )

    output_path = tmp_path / "complete_resume.pdf"

    render_final_resume_pdf(
        resume,
        output_path,
    )

    assert output_path.exists()
    assert output_path.stat().st_size > 0
    assert output_path.read_bytes().startswith(b"%PDF")


def test_render_final_resume_pdf_preserves_section_order(
    monkeypatch,
    tmp_path,
):
    resume = FinalResume(
        personal_info=valid_personal_info(),
        summary="Summary",
        skills=["Python"],
        experience=[
            {
                "job_title": "AI Engineer",
                "company": "Example",
            }
        ],
        projects=[
            {
                "title": "AI Resume Analyzer",
            }
        ],
        education=[
            {
                "degree": "B.Tech",
            }
        ],
        certifications=[
            {
                "name": "Python Certification",
            }
        ],
        section_order=[
            "skills",
            "summary",
            "projects",
            "experience",
            "education",
            "certifications",
        ],
    )

    captured_headings = []

    def fake_add_section_heading(
        story,
        styles,
        title,
    ):
        captured_headings.append(title)

    monkeypatch.setattr(
        "app.resume_pdf_renderer._add_section_heading",
        fake_add_section_heading,
    )

    render_final_resume_pdf(
        resume,
        tmp_path / "ordered.pdf",
    )

    assert captured_headings == [
        "Skills",
        "Professional Summary",
        "Projects",
        "Experience",
        "Education",
        "Certifications",
    ]


def test_render_final_resume_pdf_does_not_mutate_resume(
    tmp_path,
):
    resume = FinalResume(
        personal_info={
            "name": "Chandu",
            "email": "chandu@example.com",
        },
        summary="AI Engineer",
        skills=[
            "Python",
            "Machine Learning",
        ],
        experience=[
            {
                "job_title": "AI Engineer",
                "company": "Example",
                "bullets": [
                    "Built AI systems.",
                ],
            }
        ],
    )

    before = resume.to_dict()

    render_final_resume_pdf(
        resume,
        tmp_path / "resume.pdf",
    )

    after = resume.to_dict()

    assert after == before


def test_render_final_resume_pdf_escapes_markup_characters(
    tmp_path,
):
    resume = FinalResume(
        personal_info={
            "name": "A & B <Engineer>",
        },
        summary=(
            "AI & ML engineer working with "
            "<Python> and data."
        ),
        skills=[
            "C++",
            "A & B",
        ],
    )

    output_path = tmp_path / "escaped.pdf"

    render_final_resume_pdf(
        resume,
        output_path,
    )

    assert output_path.exists()
    assert output_path.stat().st_size > 0
    assert output_path.read_bytes().startswith(b"%PDF")


def test_render_final_resume_pdf_handles_bullet_markers(
    tmp_path,
):
    resume = FinalResume(
        personal_info=valid_personal_info(),
        experience=[
            {
                "job_title": "AI Engineer",
                "bullets": [
                    "• Built ML models.",
                    "- Developed RAG pipelines.",
                    "– Created ATS analysis.",
                    "— Improved resume matching.",
                ],
            }
        ],
    )

    output_path = tmp_path / "bullets.pdf"

    render_final_resume_pdf(
        resume,
        output_path,
    )

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_render_final_resume_pdf_creates_parent_directory(
    tmp_path,
):
    resume = FinalResume(
        personal_info=valid_personal_info(),
        summary="AI Engineer",
    )

    output_path = (
        tmp_path
        / "generated"
        / "resumes"
        / "optimized.pdf"
    )

    result = render_final_resume_pdf(
        resume,
        output_path,
    )

    assert result == output_path
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_render_final_resume_pdf_supports_empty_resume(
    tmp_path,
):
    # An actually empty FinalResume is invalid when validation
    # is enabled because the validator requires a candidate name.
    resume = FinalResume()

    output_path = tmp_path / "empty.pdf"

    result = render_final_resume_pdf(
        resume,
        output_path,
        validate=False,
    )

    assert result == output_path
    assert output_path.exists()
    assert output_path.stat().st_size > 0

