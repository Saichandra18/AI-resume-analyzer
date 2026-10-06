def build_rewrite_input(
    resume_text,
    resume_data=None,
    tailoring_plan=None,
    job_description="",
):
    """Build the input payload for resume rewriting."""

    return {
        "resume_text": resume_text or "",
        "resume_data": resume_data or {},
        "tailoring_plan": tailoring_plan or {},
        "job_description": job_description or "",
    }


def build_rewrite_output(
    summary=None,
    experience=None,
    projects=None,
    skills=None,
    validation=None,
):
    """Build a normalized resume rewrite result."""

    return {
        "summary": summary or {},
        "experience": experience or [],
        "projects": projects or [],
        "skills": skills or {},
        "validation": validation or {
            "meaning_preserved": False,
            "unsupported_claims": [],
            "grounding_status": "unverified",
        },
    }