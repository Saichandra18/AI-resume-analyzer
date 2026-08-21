import re


def clean_resume_text(text):
    """Clean and normalize extracted resume text."""

    if not text:
        return ""

    # Replace escaped Unicode characters
    text = text.replace("\\u2014", "—")
    text = text.replace("\\u2022", "•")
    text = text.replace("\\u2013", "–")

    # Replace multiple spaces with a single space
    text = re.sub(r"[ \t]+", " ", text)

    # Remove spaces before punctuation
    text = re.sub(r"\s+([,.;:])", r"\1", text)

    # Normalize excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove spaces around newlines
    text = re.sub(r" *\n *", "\n", text)

    return text.strip()