"""Document loading for the RAG knowledge base."""

from pathlib import Path


class DocumentLoader:
    """Load supported document formats into raw text."""

    SUPPORTED_EXTENSIONS = {
        ".txt",
        ".md",
        ".pdf",
        ".docx",
    }

    def load(self, file_path):
        """Load a document and return its raw text."""

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Document not found: {file_path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Document path is not a file: {file_path}"
            )

        extension = path.suffix.lower()

        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported document type: {extension}"
            )

        if extension in {".txt", ".md"}:
            return self._load_text(path)

        if extension == ".pdf":
            return self._load_pdf(path)

        if extension == ".docx":
            return self._load_docx(path)

        raise ValueError(
            f"Unsupported document type: {extension}"
        )

    @staticmethod
    def _load_text(path):
        """Load plain-text or Markdown content."""

        return path.read_text(
            encoding="utf-8"
        )

    @staticmethod
    def _load_pdf(path):
        """Load text from a PDF document."""

        from PyPDF2 import PdfReader

        reader = PdfReader(str(path))

        pages = []

        for page in reader.pages:
            text = page.extract_text()

            if text:
                pages.append(text)

        return "\n".join(pages)

    @staticmethod
    def _load_docx(path):
        """Load text from a DOCX document."""

        from docx import Document

        document = Document(str(path))

        paragraphs = [
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text
        ]

        return "\n".join(paragraphs)