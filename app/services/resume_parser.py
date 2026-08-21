from pathlib import Path
from pypdf import PdfReader
from docx import Document

from app.resume_structurer import structure_resume


def extract_text_from_pdf(file_path):
    """Extract text from a PDF resume."""
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

    raise ValueError("Unsupported file format. Use PDF or DOCX.")

def extract_structured_resume(file_path):
    """Extract and structure resume data from a PDF or DOCX file."""

    resume_text = extract_resume_text(file_path)

    return structure_resume(resume_text)