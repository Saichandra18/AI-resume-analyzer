DEGREE_FAMILIES = {
    "bachelor": {
        "bachelor",
        "bachelor's",
        "bachelor's degree",
        "b.tech",
        "btech",
        "b.e",
        "be",
        "b.sc",
        "bsc",
        "bca",
        "b.com",
        "bcom",
    },
    "master": {
        "master",
        "master's",
        "master's degree",
        "m.tech",
        "mtech",
        "m.e",
        "me",
        "m.sc",
        "msc",
        "mca",
        "mba",
        "m.com",
        "mcom",
    },
    "doctorate": {
        "ph.d",
        "phd",
        "doctorate",
    },
}


def normalize_qualification(qualification):
    """Normalize a qualification for comparison."""

    if not qualification:
        return ""

    normalized = qualification.strip().lower()

    normalized = normalized.replace(".", "")

    return normalized


def get_degree_family(qualification):
    """Return the degree family for a qualification."""

    normalized = normalize_qualification(qualification)

    for family, qualifications in DEGREE_FAMILIES.items():
        normalized_qualifications = {
            normalize_qualification(item)
            for item in qualifications
        }

        if normalized in normalized_qualifications:
            return family

    if normalized.startswith("bachelor"):
        return "bachelor"

    if normalized.startswith("master"):
        return "master"

    if normalized.startswith("doctorate"):
        return "doctorate"

    if normalized.startswith("phd"):
        return "doctorate"

    return None


def degree_matches(resume_degree, required_qualification):
    """Check whether a resume degree matches a required qualification."""

    resume_family = get_degree_family(resume_degree)
    required_family = get_degree_family(required_qualification)

    if not resume_family or not required_family:
        return False

    return resume_family == required_family


def match_qualifications(resume_degrees, required_qualifications):
    """Compare resume degrees against job qualifications."""

    resume_degrees = resume_degrees or []
    required_qualifications = required_qualifications or []

    matched = []
    missing = []

    for required_qualification in required_qualifications:
        if not required_qualification:
            continue

        found_match = any(
            degree_matches(
                resume_degree,
                required_qualification,
            )
            for resume_degree in resume_degrees
            if resume_degree
        )

        if found_match:
            if required_qualification not in matched:
                matched.append(required_qualification)
        else:
            if required_qualification not in missing:
                missing.append(required_qualification)

    return {
        "matched": matched,
        "missing": missing,
    }