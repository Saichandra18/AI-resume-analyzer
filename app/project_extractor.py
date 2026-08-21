PROJECT_SECTION_KEYWORDS = {
    "projects",
    "personal projects",
    "academic projects",
    "key projects",
    "projects & achievements",
    "projects and achievements",
}


END_SECTION_KEYWORDS = {
    "experience",
    "work experience",
    "professional experience",
    "education",
    "skills",
    "technical skills",
    "certifications",
    "achievements",
    "awards",
    "languages",
    "interests",
    "references",
}


def find_project_section(text):
    """Find the projects section and return its lines."""

    if not text:
        return []

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    start_index = None

    for index, line in enumerate(lines):
        if line.lower().strip(":") in PROJECT_SECTION_KEYWORDS:
            start_index = index + 1
            break

    if start_index is None:
        return []

    project_lines = []

    for line in lines[start_index:]:
        line_lower = line.lower().strip(":")

        if line_lower in END_SECTION_KEYWORDS:
            break

        project_lines.append(line)

    return project_lines