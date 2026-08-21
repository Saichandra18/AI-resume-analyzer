CERTIFICATION_SECTION_KEYWORDS = {
    "certifications",
    "certificates",
    "professional certifications",
    "licenses & certifications",
    "licenses and certifications",
}


END_SECTION_KEYWORDS = {
    "experience",
    "work experience",
    "professional experience",
    "education",
    "skills",
    "technical skills",
    "projects",
    "achievements",
    "awards",
    "languages",
    "interests",
    "references",
}


def find_certification_section(text):
    """Find the certification section and return its lines."""

    if not text:
        return []

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    start_index = None

    for index, line in enumerate(lines):
        if line.lower().strip(":") in CERTIFICATION_SECTION_KEYWORDS:
            start_index = index + 1
            break

    if start_index is None:
        return []

    certification_lines = []

    for line in lines[start_index:]:
        line_lower = line.lower().strip(":")

        if line_lower in END_SECTION_KEYWORDS:
            break

        certification_lines.append(line)

    return certification_lines