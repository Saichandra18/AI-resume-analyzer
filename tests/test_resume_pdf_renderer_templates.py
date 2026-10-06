from pathlib import Path

from app.final_resume_models import FinalResume
from app.resume_pdf_renderer import render_final_resume_pdf
from app.templates.registry import get_template


def valid_resume():
    return FinalResume(
        personal_info={
            "name": "Chandu",
            "email": "chandu@example.com",
            "phone": "9876543210",
            "location": "India",
        },
        summary="AI/ML Engineer specializing in Generative AI and RAG.",
        skills=["Python", "SQL", "Machine Learning", "RAG"],
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
    )


def test_pdf_template_registry_contains_professional_templates():
    assert get_template("ats_clean").name == "ats_clean"
    assert get_template("modern").name == "modern"
    assert get_template("technical").name == "technical"


def test_pdf_ats_clean_template_generates_pdf(tmp_path):
    output = tmp_path / "ats_clean.pdf"

    result = render_final_resume_pdf(
        valid_resume(),
        output,
        template="ats_clean",
    )

    assert result == output
    assert output.exists()
    assert output.read_bytes().startswith(b"%PDF")
    assert output.stat().st_size > 500


def test_pdf_modern_template_generates_pdf(tmp_path):
    output = tmp_path / "modern.pdf"

    result = render_final_resume_pdf(
        valid_resume(),
        output,
        template="modern",
    )

    assert result == output
    assert output.exists()
    assert output.read_bytes().startswith(b"%PDF")
    assert output.stat().st_size > 500


def test_pdf_technical_template_generates_pdf(tmp_path):
    output = tmp_path / "technical.pdf"

    result = render_final_resume_pdf(
        valid_resume(),
        output,
        template="technical",
    )

    assert result == output
    assert output.exists()
    assert output.read_bytes().startswith(b"%PDF")
    assert output.stat().st_size > 500


def test_all_pdf_templates_are_ats_safe():
    for name in ("ats_clean", "modern", "technical"):
        template = get_template(name)
        assert template.ats_safe is True
        assert template.single_column is True


def test_pdf_templates_preserve_resume_content_and_do_not_mutate(
    tmp_path,
):
    resume = valid_resume()
    before = resume.to_dict()

    for name in ("ats_clean", "modern", "technical"):
        output = tmp_path / f"{name}.pdf"

        render_final_resume_pdf(
            resume,
            output,
            template=name,
        )

        assert output.exists()
        assert output.read_bytes().startswith(b"%PDF")

    assert resume.to_dict() == before


def test_pdf_templates_use_configured_margins(tmp_path):
    # Verify that each registered template exposes the margins used
    # by the PDF renderer.
    for name in ("ats_clean", "modern", "technical"):
        template = get_template(name)

        assert template.top_margin > 0
        assert template.bottom_margin > 0
        assert template.left_margin > 0
        assert template.right_margin > 0


def test_pdf_templates_have_distinct_formatting_profiles():
    ats = get_template("ats_clean")
    modern = get_template("modern")
    technical = get_template("technical")

    assert ats.name == "ats_clean"
    assert modern.name == "modern"
    assert technical.name == "technical"

    assert ats.body_font_size != technical.body_font_size
    assert modern.heading_font_size != technical.heading_font_size
    assert ats.name_alignment != modern.name_alignment
