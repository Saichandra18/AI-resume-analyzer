import re


def clean_job_description(text):
    """Clean and normalize job description text."""

    if not text:
        return ""

    # Replace escaped Unicode characters
    text = text.replace("\\u2014", "—")
    text = text.replace("\\u2022", "•")
    text = text.replace("\\u2013", "–")

    # Normalize Windows and carriage-return newlines
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Replace multiple spaces and tabs with a single space
    text = re.sub(r"[ \t]+", " ", text)

    # Remove spaces before punctuation
    text = re.sub(r"\s+([,.;:])", r"\1", text)

    # Normalize excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove spaces around newlines
    text = re.sub(r" *\n *", "\n", text)

    return text.strip()