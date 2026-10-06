"""Text cleaning for the RAG knowledge base."""

import re


class DocumentCleaner:
    """Clean normalized document text for downstream RAG processing."""

    def clean(self, text):
        """Return cleaned document text."""

        if text is None:
            raise ValueError("Document text cannot be None.")

        if not isinstance(text, str):
            raise TypeError("Document text must be a string.")

        text = text.replace("\u00a0", " ")

        # Normalize whitespace inside lines.
        lines = [
            re.sub(r"[ \t]+", " ", line).strip()
            for line in text.split("\n")
        ]

        # Remove empty lines.
        lines = [
            line
            for line in lines
            if line
        ]

        text = "\n".join(lines)

        # Normalize repeated separator characters.
        text = re.sub(r"[=_-]{4,}", "---", text)

        return text.strip()