from copy import deepcopy
from pathlib import Path

import pytest
from pypdf import PdfReader

from app.final_resume_models import FinalResume
from app.resume_pdf_renderer import (
    _build_styles,
    render_final_resume_pdf,
)
from app.templates.registry import get_template


TEMPLATES = ("ats_clean", "modern", "technical")


def build_resume():
    """Build a representative FinalResume for PDF validation."""
    return FinalResume(
        personal_info={
            "name": "Test Candidate",
            "email": "test@example.com",
            "phone": "9876543210",
            "location": "India",
            "linkedin": "linkedin.com/in/test",
            "github": "github.com/test",
            "website": "test.dev",
        },
        summary="AI/ML Engineer focused on Python, machine learning, and Generative AI.",
        skills=["Python", "Machine Learning", "SQL", "Generative AI", "RAG"],
        experience=[
            {
                "job_title": "AI/ML Engineer",
                "company": "Example Technologies",
                "location": "India",
                "dates": "2024 - Present",
                "bullets": [
                    "Built machine learning pipelines using Python and scikit-learn.",
                    "Implemented retrieval-augmented generation workflows.",
                ],
            }
        ],
        projects=[
            {
                "title": "AI Resume Analyzer",
                "description": "Analyzes resumes against job descriptions and generates optimization recommendations.",
                "bullets": [
                    "Implemented ATS scoring and skill-gap analysis.",
                    "Added RAG grounding and optimized resume generation.",
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


def pdf_text(path):
    """Extract text from every PDF page."""
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


@pytest.mark.parametrize("template", TEMPLATES)
def test_all_templates_generate_openable_pdf(tmp_path, template):
    resume = build_resume()
    output_path = tmp_path / f"{template}.pdf"

    result = render_final_resume_pdf(
        resume,
        output_path,
        template=template,
    )

    assert result == output_path
    assert output_path.exists()
    assert output_path.stat().st_size > 0
    assert output_path.read_bytes().startswith(b"%PDF")

    reader = PdfReader(str(output_path))
    assert len(reader.pages) >= 1
    assert reader.pages[0].extract_text() is not None


@pytest.mark.parametrize("template", TEMPLATES)
def test_all_templates_preserve_resume_content(tmp_path, template):
    resume = build_resume()
    output_path = tmp_path / f"{template}.pdf"

    render_final_resume_pdf(
        resume,
        output_path,
        template=template,
    )

    text = pdf_text(output_path)

    expected_values = [
        "Test Candidate",
        "test@example.com",
        "9876543210",
        "AI/ML Engineer",
        "Machine Learning",
        "Generative AI",
        "AI Resume Analyzer",
        "B.Tech in Computer Science",
        "Machine Learning Certification",
    ]

    for value in expected_values:
        assert value in text


@pytest.mark.parametrize("template", TEMPLATES)
def test_all_templates_preserve_section_order(tmp_path, template):
    resume = build_resume()
    output_path = tmp_path / f"{template}.pdf"

    render_final_resume_pdf(
        resume,
        output_path,
        template=template,
    )

    text = pdf_text(output_path).upper()

    positions = [
        text.index("SUMMARY"),
        text.index("SKILLS"),
        text.index("EXPERIENCE"),
        text.index("PROJECTS"),
        text.index("EDUCATION"),
        text.index("CERTIFICATIONS"),
    ]

    assert positions == sorted(positions)


@pytest.mark.parametrize("template", TEMPLATES)
def test_all_templates_are_ats_safe_single_column(tmp_path, template):
    config = get_template(template)

    assert config.ats_safe is True
    assert config.single_column is True

    resume = build_resume()
    output_path = tmp_path / f"{template}.pdf"

    render_final_resume_pdf(
        resume,
        output_path,
        template=template,
    )

    reader = PdfReader(str(output_path))
    assert len(reader.pages) >= 1

    # The renderer builds the resume from paragraphs only; verify that
    # the generated PDF remains text-extractable as a single-column document.
    text = pdf_text(output_path)
    assert "Test Candidate" in text
    assert "AI Resume Analyzer" in text


@pytest.mark.parametrize("template", TEMPLATES)
def test_template_typography_is_applied_to_pdf_styles(template):
    config = get_template(template)
    styles = _build_styles(config)

    assert styles["name"].fontSize == config.name_font_size
    assert styles["contact"].fontSize == config.contact_font_size
    assert styles["heading"].fontSize == config.heading_font_size
    assert styles["body"].fontSize == config.body_font_size
    assert styles["title"].fontSize == config.item_title_font_size
    assert styles["secondary"].fontSize == config.secondary_font_size
    assert styles["bullet"].fontSize == config.body_font_size


@pytest.mark.parametrize("template", TEMPLATES)
def test_template_margins_and_spacing_are_applied_to_pdf_styles(template):
    config = get_template(template)
    styles = _build_styles(config)

    assert styles["heading"].spaceBefore == config.section_space_before
    assert styles["heading"].spaceAfter == config.section_space_after
    assert styles["body"].spaceAfter == config.body_space_after
    assert styles["title"].spaceBefore == config.section_space_after
    assert styles["secondary"].spaceAfter == config.body_space_after
    assert styles["bullet"].spaceAfter == config.body_space_after

    assert config.top_margin > 0
    assert config.bottom_margin > 0
    assert config.left_margin > 0
    assert config.right_margin > 0


@pytest.mark.parametrize("template", TEMPLATES)
def test_pdf_rendering_does_not_mutate_final_resume(tmp_path, template):
    resume = build_resume()
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
def test_pdf_rendering_preserves_page_readability(tmp_path, template):
    resume = build_resume()
    output_path = tmp_path / f"{template}.pdf"

    render_final_resume_pdf(
        resume,
        output_path,
        template=template,
    )

    reader = PdfReader(str(output_path))

    assert len(reader.pages) >= 1

    for page in reader.pages:
        text = page.extract_text() or ""
        assert text.strip()
        assert "Test Candidate" in text or len(reader.pages) > 1
