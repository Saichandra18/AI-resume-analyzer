REQUIRED_COMPONENTS = (
    "name",
    "email",
    "phone",
    "skills",
    "education",
    "experience",
    "projects",
)

OPTIONAL_COMPONENTS = (
    "certifications",
)


def _is_present(value):
    """Return True when a resume value contains usable data."""

    if value is None:
        return False

    if isinstance(value, str):
        return bool(value.strip())

    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)

    return bool(value)


def _component_presence(resume_data):
    """Determine whether each resume component is present."""

    personal_info = resume_data.get(
        "personal_info",
        {}
    ) or {}

    education = resume_data.get(
        "education",
        {}
    ) or {}

    experience = resume_data.get(
        "experience",
        {}
    ) or {}

    return {
        "name": _is_present(
            personal_info.get("name")
        ),
        "email": _is_present(
            personal_info.get("email")
        ),
        "phone": _is_present(
            personal_info.get("phone")
        ),
        "skills": _is_present(
            resume_data.get("skills")
        ),
        "education": _is_present(
            education.get("section")
        ) or _is_present(
            education.get("degrees")
        ),
        "experience": _is_present(
            experience.get("section")
        ) or _is_present(
            experience.get("job_titles")
        ),
        "projects": _is_present(
            resume_data.get("projects")
        ),
        "certifications": _is_present(
            resume_data.get("certifications")
        ),
    }


def analyze_resume_quality(resume_data):
    """Analyze structural completeness of a resume."""

    if not resume_data:
        resume_data = {}

    presence = _component_presence(resume_data)

    required_count = len(REQUIRED_COMPONENTS)

    present_required_count = sum(
        presence[component]
        for component in REQUIRED_COMPONENTS
    )

    score = round(
        (present_required_count / required_count) * 100
    )

    missing_sections = [
        component
        for component in REQUIRED_COMPONENTS
        if not presence[component]
    ]

    components = {}

    component_score = 100 / required_count

    for component in REQUIRED_COMPONENTS:
        components[component] = {
            "present": presence[component],
            "score": round(
                component_score
                if presence[component]
                else 0.0,
                2,
            ),
        }

    optional_sections = {
        component: {
            "present": presence[component]
        }
        for component in OPTIONAL_COMPONENTS
    }

    return {
        "score": score,
        "components": components,
        "missing_sections": missing_sections,
        "optional_sections": optional_sections,
    }