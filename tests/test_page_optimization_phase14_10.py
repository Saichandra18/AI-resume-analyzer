from copy import deepcopy

import pytest
from docx import Document
from pypdf import PdfReader

from app.final_resume_models import FinalResume
from app.resume_document_renderer import render_final_resume
from app.resume_pdf_renderer import render_final_resume_pdf
from app.templates.registry import get_template


TEMPLATES = ("ats_clean", "modern", "technical")


def build_compact_resume():
    """Build a representative one-page resume."""
    return FinalResume(
        personal_info={
            "name": "Test Candidate",
            "email": "test@example.com",
            "phone": "9876543210",
            "location": "India",
        },
        summary=(
            "AI/ML Engineer focused on Python, machine learning, "
            "Generative AI, and RAG."
        ),
        skills=[
            "Python",
            "Machine Learning",
            "SQL",
            "Generative AI",
            "RAG",
        ],
        experience=[
            {
                "job_title": "AI/ML Engineer",
                "company": "Example Technologies",
                "dates": "2024 - Present",
                "bullets": [
                    "Built machine learning pipelines using Python.",
                    "Implemented RAG workflows for resume optimization.",
                ],
            }
        ],
        projects=[
            {
                "title": "AI Resume Analyzer",
                "description": "Analyzes resumes against job descriptions.",
                "bullets": [
                    "Implemented ATS scoring and skill-gap analysis.",
                    "Added grounded resume generation.",
                ],
            }
        ],
        education=[
            {
                "degree": "B.Tech in Computer Science",
                "institution": "Example University",
                "dates": "2020 - 2024",
            }
        ],
        certifications=[
            {
                "name": "Machine Learning Certification",
                "organization": "Example Institute",
                "year": "2024",
            }
        ],
    )


def build_long_resume():
    """Build a deliberately content-heavy resume for pagination tests."""
    resume = build_compact_resume()

    resume.experience = [
        {
            "job_title": f"AI/ML Engineer {index}",
            "company": "Example Technologies",
            "dates": "2020 - Present",
            "bullets": [
                (
                    f"Built production machine learning pipelines and "
                    f"automated data workflows for project {index}."
                ),
                (
                    f"Implemented Python, SQL, RAG, and Generative AI "
                    f"solutions for project {index}."
                ),
                (
                    f"Improved model evaluation, data processing, and "
                    f"deployment workflows for project {index}."
                ),
                (
                    f"Created monitoring and validation processes for "
                    f"project {index}."
                ),
            ],
        }
        for index in range(1, 13)
    ]

    resume.projects = [
        {
            "title": f"Machine Learning Project {index}",
            "description": (
                "End-to-end machine learning and Generative AI project "
                "covering data preparation, modeling, evaluation, and "
                "deployment."
            ),
            "bullets": [
                "Implemented data processing and model evaluation.",
                "Added automated validation and reporting.",
            ],
        }
        for index in range(1, 9)
    ]

    resume.education = [
        {
            "degree": f"Computer Science Degree {index}",
            "institution": "Example University",
            "dates": "2018 - 2024",
        }
        for index in range(1, 5)
    ]

    resume.certifications = [
        {
            "name": f"Professional Certification {index}",
            "organization": "Example Institute",
            "year": "2024",
        }
        for index in range(1, 8)
    ]

    return resume


def pdf_page_count(path):
    """Return the number of pages in a PDF."""
    return len(PdfReader(str(path)).pages)


def pdf_text(path):
    """Extract all PDF text."""
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


@pytest.mark.parametrize("template", TEMPLATES)
def test_compact_resume_stays_within_reasonable_page_count(
    tmp_path,
    template,
):
    resume = build_compact_resume()
    output_path = tmp_path / f"{template}.pdf"

    render_final_resume_pdf(
        resume,
        output_path,
        template=template,
    )

    assert 1 <= pdf_page_count(output_path) <= 2


@pytest.mark.parametrize("template", TEMPLATES)
def test_long_resume_paginates_without_blank_pages(
    tmp_path,
    template,
):
    resume = build_long_resume()
    output_path = tmp_path / f"{template}.pdf"

    render_final_resume_pdf(
        resume,
        output_path,
        template=template,
    )

    reader = PdfReader(str(output_path))

    assert len(reader.pages) >= 2

    for page in reader.pages:
        assert (page.extract_text() or "").strip()


@pytest.mark.parametrize("template", TEMPLATES)
def test_long_resume_preserves_content_across_pages(
    tmp_path,
    template,
):
    resume = build_long_resume()
    output_path = tmp_path / f"{template}.pdf"

    render_final_resume_pdf(
        resume,
        output_path,
        template=template,
    )

    text = pdf_text(output_path)

    assert "Test Candidate" in text
    assert "AI/ML Engineer 1" in text
    assert "AI/ML Engineer 12" in text
    assert "Machine Learning Project 1" in text
    assert "Machine Learning Project 8" in text
    assert "Professional Certification 7" in text


@pytest.mark.parametrize("template", TEMPLATES)
def test_long_resume_does_not_create_unexpected_empty_trailing_page(
    tmp_path,
    template,
):
    resume = build_long_resume()
    output_path = tmp_path / f"{template}.pdf"

    render_final_resume_pdf(
        resume,
        output_path,
        template=template,
    )

    reader = PdfReader(str(output_path))

    assert len(reader.pages) >= 2
    final_page_text = reader.pages[-1].extract_text() or ""
    assert final_page_text.strip()


@pytest.mark.parametrize("template", TEMPLATES)
def test_template_margins_are_compatible_with_page_layout(
    template,
):
    config = get_template(template)

    assert config.top_margin + config.bottom_margin < 11
    assert config.left_margin + config.right_margin < 8.5


@pytest.mark.parametrize("template", TEMPLATES)
def test_docx_page_layout_uses_template_margins(
    tmp_path,
    template,
):
    resume = build_compact_resume()
    output_path = tmp_path / f"{template}.docx"

    render_final_resume(
        resume,
        output_path,
        template=template,
    )

    document = Document(output_path)
    section = document.sections[0]

    assert section.top_margin.inches == pytest.approx(
        get_template(template).top_margin
    )
    assert section.bottom_margin.inches == pytest.approx(
        get_template(template).bottom_margin
    )
    assert section.left_margin.inches == pytest.approx(
        get_template(template).left_margin
    )
    assert section.right_margin.inches == pytest.approx(
        get_template(template).right_margin
    )


@pytest.mark.parametrize("template", TEMPLATES)
def test_page_optimization_does_not_mutate_resume(
    tmp_path,
    template,
):
    resume = build_long_resume()
    before = deepcopy(resume)

    output_path = tmp_path / f"{template}.pdf"

    render_final_resume_pdf(
        resume,
        output_path,
        template=template,
    )

    assert resume.personal_info == before.personal_info
    assert resume.summary == before.summary
    assert resume.skills == before.skills
    assert resume.experience == before.experience
    assert resume.projects == before.projects
    assert resume.education == before.education
    assert resume.certifications == before.certifications
    assert resume.section_order == before.section_order
    assert resume.metadata.__dict__ == before.metadata.__dict__


@pytest.mark.parametrize("template", TEMPLATES)
def test_page_optimization_keeps_single_column_configuration(
    template,
):
    config = get_template(template)

    assert config.single_column is True
    assert config.ats_safe is True
