
import re


EDUCATION_KEYWORDS = {
    "education",
    "academic background",
    "academic qualifications",
    "qualifications",
    "educational background",
}


DEGREE_KEYWORDS = {
    "bachelor",
    "b.tech",
    "btech",
    "b.e",
    "be",
    "b.sc",
    "bsc",
    "b.com",
    "bca",
    "master",
    "m.tech",
    "mtech",
    "m.e",
    "me",
    "m.sc",
    "msc",
    "m.com",
    "mca",
    "mba",
    "phd",
    "doctorate",
    "diploma",
}


def _normalize_degree_text(text):
    """
    Normalize common PDF text-extraction spacing artifacts
    in degree names.

    Some PDF extractors incorrectly split characters inside
    words, for example:

        T echnology -> Technology
        B.T ech      -> B.Tech

    Only known degree-related artifacts are normalized so that
    unrelated resume text is not modified.
    """

    if not text:
        return ""

    normalized = str(text).strip()

    replacements = {
        "T echnology": "Technology",
        "t echnology": "technology",
        "B.T ech": "B.Tech",
        "b.t ech": "b.tech",
        "B. T ech": "B.Tech",
        "b. t ech": "b.tech",
    }

    for incorrect, correct in replacements.items():
        normalized = normalized.replace(
            incorrect,
            correct,
        )

    return normalized


def find_education_section(text):
    """Find the education section and return its lines."""

    if not text:
        return []

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    start_index = None

    for index, line in enumerate(lines):
        if line.lower().strip(":") in EDUCATION_KEYWORDS:
            start_index = index + 1
            break

    if start_index is None:
        return []

    section_lines = []

    for line in lines[start_index:]:
        line_lower = line.lower().strip(":")

        if line_lower in {
            "experience",
            "work experience",
            "professional experience",
            "projects",
            "skills",
            "certifications",
            "professional certifications",
            "achievements",
        }:
            break

        section_lines.append(line)

    return section_lines


def extract_degrees(text):
    """Extract normalized degree lines from the education section."""

    section_lines = find_education_section(text)

    if section_lines:
        lines = section_lines
    else:
        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

    degrees = []

    for line in lines:
        normalized_line = _normalize_degree_text(
            line
        )

        line_lower = normalized_line.lower()

        if any(
            keyword in line_lower
            for keyword in DEGREE_KEYWORDS
        ):
            degrees.append(normalized_line)

    return degrees


def extract_education_years(text):
    """Extract four-digit education-related years."""

    if not text:
        return []

    section_lines = find_education_section(text)

    if section_lines:
        section_text = " ".join(section_lines)
    else:
        section_text = text

    years = re.findall(
        r"\b(?:19|20)\d{2}\b",
        section_text,
    )

    return list(dict.fromkeys(years))

