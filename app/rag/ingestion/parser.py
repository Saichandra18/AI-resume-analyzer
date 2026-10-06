"""Text parsing for the RAG knowledge base."""

import re


class DocumentParser:
    """Parse raw document text into normalized text."""

    def parse(self, text):
        """Parse and normalize raw document text."""

        if text is None:
            raise ValueError("Document text cannot be None.")

        if not isinstance(text, str):
            raise TypeError("Document text must be a string.")

        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        lines = [
            self._normalize_line(line)
            for line in text.split("\n")
        ]

        lines = [
            line
            for line in lines
            if line
        ]

        return "\n".join(lines)

    @staticmethod
    def _normalize_line(line):
        """Normalize whitespace within a single line."""

        line = line.strip()
        line = re.sub(r"[ \t]+", " ", line)

        return line