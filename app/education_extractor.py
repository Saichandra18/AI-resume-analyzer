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


def find_education_section(text):
    """Find the education section and return its lines."""

    if not text:
        return []

    lines = [line.strip() for line in text.splitlines() if line.strip()]

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
            "achievements",
        }:
            break

        section_lines.append(line)

    return section_lines


def extract_degrees(text):
    """Extract lines that appear to contain degree information."""

    if not text:
        return []

    lines = text.splitlines()
    degrees = []

    for line in lines:
        line_lower = line.lower()

        if any(keyword in line_lower for keyword in DEGREE_KEYWORDS):
            degrees.append(line.strip())

    return degrees


def extract_education_years(text):
    """Extract four-digit education-related years."""

    if not text:
        return []

    years = re.findall(r"\b(?:19|20)\d{2}\b", text)

    return list(dict.fromkeys(years))
