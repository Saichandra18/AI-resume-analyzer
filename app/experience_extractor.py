import re


EXPERIENCE_SECTION_KEYWORDS = {
    "experience",
    "work experience",
    "professional experience",
    "employment history",
    "work history",
}


END_SECTION_KEYWORDS = {
    "education",
    "skills",
    "technical skills",
    "core competencies",
    "projects",
    "certifications",
    "professional certifications",
    "achievements",
    "awards",
    "languages",
    "interests",
    "references",
}


JOB_TITLE_KEYWORDS = {
    "analyst",
    "developer",
    "engineer",
    "manager",
    "consultant",
    "intern",
    "designer",
    "administrator",
    "specialist",
    "scientist",
    "architect",
    "lead",
    "associate",
    "executive",
    "trainer",
}


def find_experience_section(text):
    """Find the work experience section and return its lines."""

    if not text:
        return []

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    start_index = None

    for index, line in enumerate(lines):
        if (
            line.lower().strip(":")
            in EXPERIENCE_SECTION_KEYWORDS
        ):
            start_index = index + 1
            break

    if start_index is None:
        return []

    section_lines = []

    for line in lines[start_index:]:
        line_lower = line.lower().strip(":")

        if line_lower in END_SECTION_KEYWORDS:
            break

        section_lines.append(line)

    return section_lines
def _normalize_job_title_text(text):
    """Normalize common PDF text-extraction spacing artifacts."""

    if not text:
        return ""

    normalized = text.strip()

    # Repair characters that PDF extraction may split with spaces.
    replacements = {
        "F reelance": "Freelance",
        "L LM": "LLM",
        "T rainer": "Trainer",
    }

    for incorrect, correct in replacements.items():
        normalized = normalized.replace(incorrect, correct)

    return normalized

def extract_job_titles(text):
    """Extract job-title lines from the experience section."""

    section_lines = find_experience_section(text)

    if section_lines:
        lines = section_lines
    else:
        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

    job_titles = []

    for line in lines:
        line_clean = line.strip()

        # Skip responsibility bullets.
        if line_clean.startswith(("•", "", "-", "–", "—")):
            continue

        normalized = _normalize_job_title_text(line_clean)
        line_lower = normalized.lower()

        if any(
            keyword in line_lower
            for keyword in JOB_TITLE_KEYWORDS
        ):
            job_titles.append(normalized)

    return job_titles

def extract_experience_years(text):
    """Extract year ranges from the experience section."""

    if not text:
        return []

    section_lines = find_experience_section(text)

    if section_lines:
        section_text = " ".join(section_lines)
    else:
        section_text = text

    pattern = (
        r"\b(?:19|20)\d{2}\b"
        r"(?:\s*[-–]\s*"
        r"(?:Present|Current|\b(?:19|20)\d{2}\b))?"
    )

    matches = re.findall(
        pattern,
        section_text,
        re.IGNORECASE,
    )

    return list(dict.fromkeys(matches))

