def generate_recommendations(ats_result):
    """Generate actionable recommendations from ATS gaps."""

    if not ats_result:
        return {
            "recommendations": []
        }

    recommendations = []

    missing_skills = ats_result.get("missing_skills", [])
    missing_qualifications = ats_result.get(
        "missing_qualifications", []
    )
    missing_keywords = ats_result.get("missing_keywords", [])

    for skill in missing_skills:
        recommendations.append({
            "type": "skill",
            "item": skill,
            "recommendation": (
                f"Consider highlighting relevant {skill} "
                "experience if applicable."
            ),
        })

    for qualification in missing_qualifications:
        recommendations.append({
            "type": "qualification",
            "item": qualification,
            "recommendation": (
                f"Consider highlighting your {qualification} "
                "qualification if applicable."
            ),
        })

    for keyword in missing_keywords:
        recommendations.append({
            "type": "keyword",
            "item": keyword,
            "recommendation": (
                f"Consider naturally incorporating the keyword "
                f"'{keyword}' if it accurately reflects your "
                "experience."
            ),
        })

    return {
        "recommendations": recommendations
    }