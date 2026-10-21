"""PDF rendering for validated final resumes."""

from copy import deepcopy
from pathlib import Path

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from app.final_resume_models import FinalResume
from app.final_resume_validator import validate_final_resume
from app.templates.registry import get_template


DEFAULT_FONT_NAME = "Helvetica"
DEFAULT_FONT_SIZE = 10
DEFAULT_HEADING_SIZE = 12
DEFAULT_NAME_SIZE = 18
DEFAULT_CONTACT_SIZE = 9
DEFAULT_ITEM_TITLE_SIZE = 10.5
DEFAULT_SECONDARY_SIZE = 9

SECTION_LABELS = {
    "summary": "Professional Summary",
    "skills": "Skills",
    "experience": "Experience",
    "projects": "Projects",
    "education": "Education",
    "certifications": "Certifications",
}


def _safe_text(value):
    """Convert a value into renderable text."""

    if value is None:
        return ""

    if isinstance(value, (list, tuple, set)):
        return ", ".join(
            str(item)
            for item in value
            if item is not None
        )

    if isinstance(value, dict):
        return " | ".join(
            str(item)
            for item in value.values()
            if item is not None
        )

    return str(value)


def _escape_text(value):
    """Escape text for ReportLab Paragraph markup."""

    text = _safe_text(value)

    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _extract_name(personal_info):
    """Return the candidate name."""

    if not isinstance(personal_info, dict):
        return ""

    return _safe_text(
        personal_info.get("name", "")
    )


def _build_contact_line(personal_info):
    """Build a simple contact-information line."""

    if not isinstance(personal_info, dict):
        return ""

    values = []

    for field in (
        "email",
        "phone",
        "location",
        "linkedin",
        "github",
        "website",
    ):
        value = personal_info.get(field)

        if value:
            values.append(
                _safe_text(value)
            )

    return " | ".join(values)


def _extract_title(item):
    """Extract a useful title from a resume item."""

    if not isinstance(item, dict):
        return ""

    for field in (
        "job_title",
        "title",
        "name",
        "degree",
        "company",
    ):
        value = item.get(field)

        if value:
            return _safe_text(value)

    return ""


def _extract_secondary_line(item):
    """Extract secondary information for an item."""

    if not isinstance(item, dict):
        return ""

    values = []

    for field in (
        "company",
        "organization",
        "institution",
        "location",
        "dates",
        "date",
        "year",
        "years",
    ):
        value = item.get(field)

        if value:
            values.append(
                _safe_text(value)
            )

    return " | ".join(values)


def _clean_bullet_text(value):
    """Remove existing bullet markers."""

    text = _safe_text(value).strip()

    while text.startswith(
        ("•", "", "-", "–", "—")
    ):
        text = text[1:].strip()

    return text


def _extract_bullets(item):
    """Extract bullet-style content."""

    if isinstance(item, str):
        text = item.strip()
        return [text] if text else []

    if not isinstance(item, dict):
        text = _safe_text(item).strip()
        return [text] if text else []

    preferred_fields = (
        "bullets",
        "responsibilities",
        "achievements",
        "descriptions",
        "description",
    )

    for field in preferred_fields:
        value = item.get(field)

        if value is None:
            continue

        if isinstance(value, (list, tuple)):
            lines = [
                _safe_text(entry).strip()
                for entry in value
                if _safe_text(entry).strip()
            ]

            if lines:
                return lines

        else:
            text = _safe_text(value).strip()

            if text:
                return [text]

    return []


def _build_styles(template_config=None):
    """Build PDF paragraph styles from a template configuration."""

    styles = getSampleStyleSheet()

    config = template_config or get_template("default")

    pdf_font_map = {
        "Arial": "Helvetica",
        "Aptos": "Helvetica",
    }

    pdf_font_name = pdf_font_map.get(
        config.font_name,
        config.font_name,
    )

    name_alignment = {
        "left": 0,
        "center": TA_CENTER,
        "right": 2,
    }.get(config.name_alignment, TA_CENTER)

    contact_alignment = {
        "left": 0,
        "center": TA_CENTER,
        "right": 2,
    }.get(config.contact_alignment, TA_CENTER)

    body_leading = max(
        config.body_font_size * config.line_spacing,
        config.body_font_size,
    )

    return {
        "name": ParagraphStyle(
            "ResumeName",
            parent=styles["Normal"],
            fontName=pdf_font_name,
            fontSize=config.name_font_size,
            leading=config.name_font_size * 1.15,
            alignment=name_alignment,
            spaceBefore=0,
            spaceAfter=config.body_space_after,
        ),
        "contact": ParagraphStyle(
            "ResumeContact",
            parent=styles["Normal"],
            fontName=pdf_font_name,
            fontSize=config.contact_font_size,
            leading=config.contact_font_size * 1.2,
            alignment=contact_alignment,
            spaceBefore=0,
            spaceAfter=6,
        ),
        "heading": ParagraphStyle(
            "ResumeHeading",
            parent=styles["Normal"],
            fontName=pdf_font_name,
            fontSize=config.heading_font_size,
            leading=config.heading_font_size * 1.15,
            spaceBefore=config.section_space_before,
            spaceAfter=config.section_space_after,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "ResumeBody",
            parent=styles["Normal"],
            fontName=pdf_font_name,
            fontSize=config.body_font_size,
            leading=body_leading,
            spaceBefore=0,
            spaceAfter=config.body_space_after,
        ),
        "title": ParagraphStyle(
            "ResumeItemTitle",
            parent=styles["Normal"],
            fontName=pdf_font_name,
            fontSize=config.item_title_font_size,
            leading=config.item_title_font_size * 1.15,
            spaceBefore=config.section_space_after,
            spaceAfter=0,
            keepWithNext=True,
        ),
        "secondary": ParagraphStyle(
            "ResumeSecondary",
            parent=styles["Normal"],
            fontName=pdf_font_name,
            fontSize=config.secondary_font_size,
            leading=config.secondary_font_size * 1.15,
            spaceBefore=0,
            spaceAfter=config.body_space_after,
            keepWithNext=True,
        ),
        "bullet": ParagraphStyle(
            "ResumeBullet",
            parent=styles["Normal"],
            fontName=pdf_font_name,
            fontSize=config.body_font_size,
            leading=body_leading,
            leftIndent=12,
            firstLineIndent=-7,
            bulletIndent=0,
            spaceBefore=0,
            spaceAfter=config.body_space_after,
        ),
    }


def _add_name(story, styles, name):
    """Add candidate name."""

    if not name:
        return

    story.append(
        Paragraph(
            _escape_text(name),
            styles["name"],
        )
    )


def _add_contact_line(story, styles, contact_line):
    """Add contact information."""

    if not contact_line:
        return

    story.append(
        Paragraph(
            _escape_text(contact_line),
            styles["contact"],
        )
    )


def _add_section_heading(story, styles, title):
    """Add a resume section heading."""

    story.append(
        Paragraph(
            f"<b>{_escape_text(title)}</b>",
            styles["heading"],
        )
    )


def _add_summary(story, styles, summary):
    """Render professional summary."""

    if not summary:
        return

    story.append(
        Paragraph(
            _escape_text(summary),
            styles["body"],
        )
    )


def _add_skills(story, styles, skills):
    """Render skills."""

    if not skills:
        return

    if isinstance(skills, dict):
        values = []

        for key, value in skills.items():
            if isinstance(
                value,
                (list, tuple, set),
            ):
                items = [
                    _safe_text(item).strip()
                    for item in value
                    if _safe_text(item).strip()
                ]

                if items:
                    values.append(
                        f"{_safe_text(key)}: "
                        f"{', '.join(items)}"
                    )

            elif value:
                values.append(
                    f"{_safe_text(key)}: "
                    f"{_safe_text(value)}"
                )

    elif isinstance(skills, (list, tuple, set)):
        values = [
            _safe_text(item).strip()
            for item in skills
            if _safe_text(item).strip()
        ]

    else:
        values = [
            _safe_text(skills).strip()
        ]

    values = [
        value
        for value in values
        if value
    ]

    if not values:
        return

    story.append(
        Paragraph(
            _escape_text(", ".join(values)),
            styles["body"],
        )
    )


def _add_item(story, styles, item):
    """Render one resume item."""

    elements = []

    title = _extract_title(item)

    if title:
        elements.append(
            Paragraph(
                f"<b>{_escape_text(title)}</b>",
                styles["title"],
            )
        )

    secondary = _extract_secondary_line(item)

    if secondary:
        elements.append(
            Paragraph(
                f"<i>{_escape_text(secondary)}</i>",
                styles["secondary"],
            )
        )

    bullets = _extract_bullets(item)

    for bullet in bullets:
        cleaned_bullet = _clean_bullet_text(
            bullet
        )

        if not cleaned_bullet:
            continue

        elements.append(
            Paragraph(
                f"• {_escape_text(cleaned_bullet)}",
                styles["bullet"],
            )
        )

    if elements:
        story.append(
            KeepTogether(elements)
        )


def _add_collection(story, styles, items):
    """Render a collection of resume items."""

    for item in items or []:
        _add_item(
            story,
            styles,
            item,
        )


def _compact_template(config):
    """Copy of a template with slightly tighter vertical spacing.

    Font sizes and line spacing are untouched, so the text stays as
    readable (and ATS-friendly) as before.
    """
    compact = deepcopy(config)

    compact.section_space_before = max(config.section_space_before - 3, 3)
    compact.section_space_after = max(config.section_space_after - 1, 1)
    compact.body_space_after = max(config.body_space_after - 1, 1)
    compact.top_margin = max(config.top_margin - 0.08, 0.4)
    compact.bottom_margin = max(config.bottom_margin - 0.08, 0.4)

    return compact


def render_final_resume_pdf(
    resume,
    output_path,
    validate=True,
    template="default",
    compact=False,
):
    """
    Render a FinalResume to PDF.

    Args:
        resume: FinalResume instance.
        output_path: destination .pdf path.
        validate: validate before rendering.

    Returns:
        Path to generated PDF.
    """

    if not isinstance(
        resume,
        FinalResume,
    ):
        raise TypeError(
            "resume must be a FinalResume instance."
        )

    if validate:
        validation = validate_final_resume(
            resume
        )

        if not validation["valid"]:
            raise ValueError(
                "Cannot render invalid resume: "
                + "; ".join(
                    validation["errors"]
                )
            )

    output_path = Path(output_path)

    if output_path.suffix.lower() != ".pdf":
        raise ValueError(
            "output_path must have a .pdf extension."
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Rendering should never mutate FinalResume.
    resume = deepcopy(resume)

    template_config = get_template(template)

    if compact:
        template_config = _compact_template(template_config)

    styles = _build_styles(template_config)
    story = []

    personal_info = resume.personal_info

    name = _extract_name(personal_info)

    if name:
        _add_name(
            story,
            styles,
            name,
        )

    contact_line = _build_contact_line(
        personal_info
    )

    _add_contact_line(
        story,
        styles,
        contact_line,
    )

    section_values = {
        "summary": resume.summary,
        "skills": resume.skills,
        "experience": resume.experience,
        "projects": resume.projects,
        "education": resume.education,
        "certifications": resume.certifications,
    }

    for section in resume.section_order:
        value = section_values.get(section)

        if not value:
            continue

        heading = SECTION_LABELS.get(
            section,
            section.title(),
        )

        _add_section_heading(
            story,
            styles,
            heading,
        )

        if section == "summary":
            _add_summary(
                story,
                styles,
                value,
            )

        elif section == "skills":
            _add_skills(
                story,
                styles,
                value,
            )

        else:
            _add_collection(
                story,
                styles,
                value,
            )

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=LETTER,
        topMargin=template_config.top_margin * inch,
        bottomMargin=template_config.bottom_margin * inch,
        leftMargin=template_config.left_margin * inch,
        rightMargin=template_config.right_margin * inch,
        title=name or "Optimized Resume",
        author=name or "AI Resume Analyzer",
    )

    document.build(story)

    return output_path