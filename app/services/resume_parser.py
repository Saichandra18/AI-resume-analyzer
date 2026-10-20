import re
from pathlib import Path

from pypdf import PdfReader
from docx import Document

from app.resume_structurer import structure_resume


def _extract_pdf_text_with_pdfplumber(file_path):
    """Extract PDF text with pdfplumber, which keeps word spacing intact.

    pypdf glues words together on many resume PDFs ("ofLarge",
    "Performedprompt"). Returns "" when pdfplumber is unavailable or fails
    so the caller can fall back to pypdf.
    """
    try:
        import pdfplumber
    except ImportError:
        return ""

    try:
        with pdfplumber.open(file_path) as document:
            pages = [
                # x_tolerance=2 (default 3) keeps tightly spaced words on
                # justified lines apart ("Contributedtotraining...").
                page.extract_text(x_tolerance=2) or ""
                for page in document.pages
            ]
    except Exception:
        return ""

    text = "\n".join(pages)

    # Icon glyphs (phone, mail, LinkedIn, ...) come through as "(cid:131)".
    text = re.sub(r"\(cid:\d+\)", " ", text)

    return text.strip()


def extract_text_from_pdf(file_path):
    """Extract text from a PDF resume."""
    text = _extract_pdf_text_with_pdfplumber(file_path)

    if text:
        return text

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text.strip()


def extract_text_from_docx(file_path):
    """Extract text from a DOCX resume."""
    document = Document(file_path)

    text = ""

    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"

    return text.strip()


def extract_resume_text(file_path):
    """Extract resume text based on the file extension."""
    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)

    if extension == ".docx":
        return extract_text_from_docx(file_path)

    raise ValueError(
        "Unsupported file format. Use PDF or DOCX."
    )


def extract_structured_resume(
    file_path,
    resume_text=None,
):
    """
    Extract and structure resume data from a PDF or DOCX file.

    If resume_text is supplied, reuse it instead of parsing
    the document again.
    """

    if resume_text is None:
        resume_text = extract_resume_text(file_path)

    return structure_resume(resume_text)