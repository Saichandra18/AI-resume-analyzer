import re


EXPERIENCE_PATTERNS = [
    r"\b(?:at least|minimum of|minimum)?\s*(\d+)\+?\s+years?\s+(?:of\s+)?experience\b",
]


def extract_experience_requirement(job_description):
    """Extract minimum experience requirements from a job description."""

    if not job_description:
        return None

    match = re.search(
        EXPERIENCE_PATTERNS[0],
        job_description,
        re.IGNORECASE,
    )

    if not match:
        return None

    years = int(match.group(1))

    return {
        "min_years": years,
        "text": match.group(0).strip(),
    }