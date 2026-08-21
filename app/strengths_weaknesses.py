def generate_strengths_weaknesses(ats_result):
    """Generate user-facing strengths and weaknesses from ATS results."""

    if not ats_result:
        return {
            "strengths": [],
            "weaknesses": [],
        }

    strengths = []
    weaknesses = []

    matched_skills = ats_result.get("matched_skills", [])
    missing_skills = ats_result.get("missing_skills", [])

    experience = ats_result.get("experience") or {}

    matched_qualifications = ats_result.get(
        "matched_qualifications", []
    )
    missing_qualifications = ats_result.get(
        "missing_qualifications", []
    )

    matched_keywords = ats_result.get("matched_keywords", [])
    missing_keywords = ats_result.get("missing_keywords", [])

    for skill in matched_skills:
        strengths.append({
            "type": "skill",
            "item": skill,
            "description": (
                f"Strong skill match: {skill}."
            ),
        })

    for skill in missing_skills:
        weaknesses.append({
            "type": "skill",
            "item": skill,
            "description": (
                f"Required skill not detected: {skill}."
            ),
        })

    if experience.get("meets_requirement") is True:
        strengths.append({
            "type": "experience",
            "item": "experience",
            "description": (
                "Experience requirement is met."
            ),
        })

    elif experience.get("meets_requirement") is False:
        weaknesses.append({
            "type": "experience",
            "item": "experience",
            "description": (
                "Experience requirement is not met."
            ),
        })

    for qualification in matched_qualifications:
        strengths.append({
            "type": "qualification",
            "item": qualification,
            "description": (
                f"Required qualification matched: "
                f"{qualification}."
            ),
        })

    for qualification in missing_qualifications:
        weaknesses.append({
            "type": "qualification",
            "item": qualification,
            "description": (
                f"Required qualification not detected: "
                f"{qualification}."
            ),
        })

    for keyword in matched_keywords:
        strengths.append({
            "type": "keyword",
            "item": keyword,
            "description": (
                f"Relevant keyword matched: {keyword}."
            ),
        })

    for keyword in missing_keywords:
        weaknesses.append({
            "type": "keyword",
            "item": keyword,
            "description": (
                f"Relevant keyword not detected: {keyword}."
            ),
        })

    return {
        "strengths": strengths,
        "weaknesses": weaknesses,
    }