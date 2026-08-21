import re


QUALIFICATION_PATTERNS = [
    r"\bBachelor(?:'s)?\s+degree\b",
    r"\bMaster(?:'s)?\s+degree\b",
    r"\bB\.?Tech\.?(?!\w)",
    r"\bB\.?E\.?(?!\w)",
    r"\bB\.?Sc\.?(?!\w)",
    r"\bBCA(?!\w)",
    r"\bM\.?Tech\.?(?!\w)",
    r"\bM\.?E\.?(?!\w)",
    r"\bM\.?Sc\.?(?!\w)",
    r"\bMCA(?!\w)",
    r"\bMBA(?!\w)",
    r"\bPh\.?D\.?(?!\w)",
    r"\bDoctorate\b",
]


def extract_required_qualifications(job_description):
    """Extract educational qualifications from a job description."""

    if not job_description:
        return []

    found_qualifications = []

    for pattern in QUALIFICATION_PATTERNS:
        matches = re.findall(pattern, job_description, re.IGNORECASE)

        for match in matches:
            if match not in found_qualifications:
                found_qualifications.append(match)

    return found_qualifications